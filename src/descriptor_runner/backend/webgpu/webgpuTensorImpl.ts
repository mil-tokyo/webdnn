import { DataArrayTypes, DataType } from "../../interface/core/constants";
import { TensorImpl } from "../../core/tensorImpl";
import { WebDNNWebGPUContextImpl } from "./webgpuContextImpl";
import { WebGPUTensor } from "../../interface/backend/webgpu/webgpuTensor";

export class WebGPUTensorImpl extends TensorImpl implements WebGPUTensor {
  buffer: GPUBuffer;

  private mappedForWriteFromCPU: boolean;

  bufferSize: number; // Unit: byte

  constructor(
    private context: WebDNNWebGPUContextImpl,
    dims: ReadonlyArray<number>,
    dataType: DataType = "float32",
    public readonly forWriteFromCPU: boolean = false,
    public readonly forReadToCPU: boolean = true
  ) {
    super(dims, dataType, "webgpu");
    if (dataType !== "float32") {
      throw new Error("WebGLTensor only supports float32");
    }
    if (forWriteFromCPU && forReadToCPU) {
      throw new Error("WebGPUTensor cannot be both for read and write");
    }

    this.bufferSize = Math.max(this.length * Float32Array.BYTES_PER_ELEMENT, 4);
    let usage = GPUBufferUsage.STORAGE;
    if (forReadToCPU) {
      usage |= GPUBufferUsage.COPY_SRC;
    }
    this.buffer = this.context.device.createBuffer({
      mappedAtCreation: forWriteFromCPU,
      size: this.bufferSize,
      usage,
    });
    this.mappedForWriteFromCPU = forWriteFromCPU;
  }

  async getData(): Promise<DataArrayTypes> {
    const data: Float32Array = new Float32Array(this.length),
      dst = this.context.device.createBuffer({
        size: this.bufferSize,
        usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
      }),
      commandEncoder = this.context.device.createCommandEncoder();
    commandEncoder.copyBufferToBuffer(this.buffer, 0, dst, 0, this.bufferSize);
    this.context.device.queue.submit([commandEncoder.finish()]);
    await dst.mapAsync(GPUMapMode.READ);
    const arrayBuffer = dst.getMappedRange(),
      buffer_mapped_array = new Float32Array(arrayBuffer, 0, this.length);
    data.set(buffer_mapped_array);
    dst.unmap();
    dst.destroy();
    return data;
  }

  async setData(data: DataArrayTypes): Promise<void> {
    if (!this.mappedForWriteFromCPU) {
      throw new Error("The buffer is not mapped");
    }
    const ab = this.buffer.getMappedRange(),
      mappedArray = new Float32Array(ab);
    mappedArray.set(data);
    this.buffer.unmap();
    this.mappedForWriteFromCPU = false;
  }

  dispose(): void {
    if (this.buffer) {
      this.buffer.destroy();
    }
  }
}
