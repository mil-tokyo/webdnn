import { WebDNNCPUContext } from "../../interface/backend/cpu/cpuContext";
import {
  WasmKernelArgument,
  WebDNNWasmContext,
} from "../../interface/backend/wasm/wasmContext";
import { WasmTensor } from "../../interface/backend/wasm/wasmTensor";
import { DataArrayTypes, DataType } from "../../interface/core/constants";
import { Tensor } from "../../interface/core/tensor";
import { WasmSharedBuffer, WasmTensorImpl } from "./wasmTensorImpl";

export class WebDNNWasmContextImpl implements WebDNNWasmContext {
  backend = "wasm" as const;

  initialized = false;

  private initializing = false;

  private worker!: Worker;

  private resolvers: ((ev: MessageEvent) => boolean | undefined)[] = [];

  private wasmWorkerSrcUrl!: string;

  constructor(public cpuContext: WebDNNCPUContext) {
    if (typeof WebAssembly !== "object") {
      throw new Error("WebAssembly is not supported on this browser.");
    }
  }

  async initialize(wasmWorkerSrcUrl: string): Promise<void> {
    if (this.initialized) {
      return;
    }
    if (this.initializing) {
      throw new Error("initialize is called while initialize is running");
    }
    this.wasmWorkerSrcUrl = wasmWorkerSrcUrl;
    this.initializing = true;
    this.worker = new Worker(this.wasmWorkerSrcUrl);
    this.worker.onmessage = (ev) => {
      for (let i = 0; i < this.resolvers.length; i++) {
        if (this.resolvers[i](ev)) {
          this.resolvers.splice(i, 1);
          break;
        }
      }
    };
    this.resolvers.push((ev: MessageEvent) => {
      if (ev.data.type === "error") {
        console.error("WebAssembly Error", ev.data.message);
        return true;
      }
    });
    return new Promise((resolve) => {
      this.resolvers.push((ev: MessageEvent) => {
        if (ev.data.type === "initializeComplete") {
          this.initializing = false;
          this.initialized = true;
          resolve();
          return true;
        }
      });
    });
  }

  isWasmTensor(tensor: Tensor): tensor is WasmTensor {
    return tensor.backend === this.backend;
  }

  assertsWasmTensor(tensor: Tensor): asserts tensor is WasmTensor {
    if (tensor.backend !== this.backend) {
      throw new Error(
        `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
      );
    }
  }

  assertsWasmTensorArray(tensors: Tensor[]): asserts tensors is WasmTensor[] {
    for (const tensor of tensors) {
      if (tensor.backend !== this.backend) {
        throw new Error(
          `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
        );
      }
    }
  }

  emptyTensor(dims: ReadonlyArray<number>, dataType?: DataType): WasmTensor {
    return new WasmTensorImpl(this, dims, dataType);
  }

  async moveTensor(tensor: Tensor): Promise<WasmTensor> {
    const dst = new WasmTensorImpl(this, tensor.dims, tensor.dataType);
    await dst.setData(await tensor.getData());
    return dst;
  }

  private checkInitialized() {
    if (!this.initialized) {
      throw new Error("Not initialized");
    }
  }

  runKernel(name: string, args: WasmKernelArgument[]): void {
    const argsToSend = args.map((arg) => {
      switch (arg.type) {
        case "tensor":
          return {
            type: "tensor",
            bufferId: arg.value.sharedBuffer.backendBufferId,
          };
        default:
          return { type: "scalar", value: arg.value };
      }
    });
    this.worker.postMessage({ type: "runKernel", name, args: argsToSend });
  }

  allocBuffer(buffer: WasmSharedBuffer): void {
    this.worker.postMessage({
      type: "alloc",
      bufferId: buffer.backendBufferId,
      byteLength: buffer.byteLength,
    });
  }

  destroyBuffer(buffer: WasmSharedBuffer): void {
    this.worker.postMessage({
      type: "destroy",
      bufferId: buffer.backendBufferId,
    });
  }

  writeTensor(buffer: WasmSharedBuffer, data: DataArrayTypes): void {
    const copyData = new Uint8Array(buffer.byteLength),
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      copyDataView = new (data.constructor as any)(copyData.buffer);
    copyDataView.set(data);
    this.worker.postMessage(
      { type: "write", bufferId: buffer.backendBufferId, data: copyData },
      [copyData.buffer]
    );
  }

  readTensor(buffer: WasmSharedBuffer): Promise<Uint8Array> {
    this.worker.postMessage({ type: "read", bufferId: buffer.backendBufferId });
    return new Promise((resolve) => {
      this.resolvers.push((ev: MessageEvent) => {
        if (ev.data.type === "read") {
          resolve(ev.data.data as Uint8Array);
          return true;
        }
      });
    });
  }
}
