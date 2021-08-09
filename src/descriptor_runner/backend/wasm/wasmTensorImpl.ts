import {
  DataArrayConstructor,
  DataArrayTypes,
  DataType,
} from "../../interface/core/constants";
import { TensorImpl } from "../../core/tensorImpl";
import { WebDNNWasmContextImpl } from "./wasmContextImpl";
import {
  WasmSharedBufferInterface,
  WasmTensor,
} from "../../interface/backend/wasm/wasmTensor";
import { WebDNNLogging } from "../../logging";

const logger = WebDNNLogging.getLogger("WebDNN.WasmTensorImpl");

export class WasmSharedBuffer implements WasmSharedBufferInterface {
  private static nextBackendBufferId = 1;

  refCount: number;

  backendBufferId: number;

  constructor(
    private context: WebDNNWasmContextImpl,
    public byteLength: number
  ) {
    this.refCount = 1;
    this.backendBufferId = WasmSharedBuffer.nextBackendBufferId++;
    this.context.allocBuffer(this);
    this.context.perfTotalMemory += this.byteLength;
    logger.debug("WASM memory allocation", {
      size: this.byteLength,
      total: this.context.perfTotalMemory,
    });
  }

  incrRef(): void {
    this.refCount++;
  }

  dispose(): void {
    this.refCount--;
    if (this.refCount <= 0) {
      this.context.perfTotalMemory -= this.byteLength;
      logger.debug("WASM memory free", {
        size: this.byteLength,
        total: this.context.perfTotalMemory,
      });
      this.context.destroyBuffer(this);
    }
  }
}

export class WasmTensorImpl extends TensorImpl implements WasmTensor {
  sharedBuffer: WasmSharedBuffer;

  constructor(
    private context: WebDNNWasmContextImpl,
    dims: ReadonlyArray<number>,
    dataType: DataType = "float32",
    sharedBuffer?: WasmSharedBuffer
  ) {
    super(dims, dataType, "wasm");
    if (dataType !== "float32") {
      throw new Error("WasmTensor only supports float32");
    }
    if (sharedBuffer) {
      this.sharedBuffer = sharedBuffer;
    } else {
      this.sharedBuffer = new WasmSharedBuffer(
        this.context,
        this.length * Float32Array.BYTES_PER_ELEMENT
      );
    }
  }

  alias(dims: ReadonlyArray<number>): WasmTensorImpl {
    this.sharedBuffer.incrRef();
    return new WasmTensorImpl(
      this.context,
      dims,
      this.dataType,
      this.sharedBuffer
    );
  }

  async getData(): Promise<DataArrayTypes> {
    const buf = await this.context.readTensor(this.sharedBuffer);
    return new DataArrayConstructor[this.dataType](buf.buffer);
  }

  async setData(data: DataArrayTypes): Promise<void> {
    this.context.writeTensor(this.sharedBuffer, data);
  }

  dispose(): void {
    this.sharedBuffer.dispose();
  }
}
