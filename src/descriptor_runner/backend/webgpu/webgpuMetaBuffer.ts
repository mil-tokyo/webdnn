import { WebGPUMetaBufferContent } from "../../interface/backend/webgpu/webgpuContext";
import { WebDNNWebGPUContextImpl } from "./webgpuContextImpl";
import { WebGPUTensorImpl } from "./webgpuTensorImpl";

export class WebGPUMetaBuffer {
  constructor(
    public context: WebDNNWebGPUContextImpl,
    public tensor: WebGPUTensorImpl,
    private cpuBuffer: Uint8Array,
    private cpuBufferHash: number
  ) {}

  private static buildCPUBuffer(content: WebGPUMetaBufferContent) {
    const byteLength = content.elements.length * 4;
    const cpuBuffer = new Uint8Array(byteLength);
    const cpuBufferView = new DataView(cpuBuffer.buffer);
    let ofs = 0;
    for (const element of content.elements) {
      switch (element.type) {
        case "int32":
          cpuBufferView.setInt32(ofs, element.value, true);
          break;
        case "uint32":
          cpuBufferView.setUint32(ofs, element.value, true);
          break;
        case "float32":
          cpuBufferView.setFloat32(ofs, element.value, true);
          break;
        default:
          throw new Error();
      }
      ofs += 4;
    }

    return cpuBuffer;
  }

  private static calcBufferHash(cpuBuffer: Uint8Array): number {
    let v = 0;
    for (let i = 0; i < cpuBuffer.length; i++) {
      v += cpuBuffer[i];
    }
    return v;
  }

  private static findPooled(
    context: WebDNNWebGPUContextImpl,
    cpuBuffer: Uint8Array,
    cpuBufferHash: number
  ): WebGPUMetaBuffer | null {
    const pooled = context.pooledMetaBuffer;
    for (let i = 0; i < pooled.length; i++) {
      const item = pooled[i];
      if (
        item.cpuBuffer.length === cpuBuffer.length &&
        item.cpuBufferHash === cpuBufferHash
      ) {
        let diff = false;
        for (let j = 0; j < cpuBuffer.length; j++) {
          if (cpuBuffer[j] !== item.cpuBuffer[j]) {
            diff = true;
            break;
          }
        }
        if (!diff) {
          pooled.splice(i, 1);
          return item;
        }
      }
    }
    return null;
  }

  static async createBuffer(
    context: WebDNNWebGPUContextImpl,
    content: WebGPUMetaBufferContent
  ): Promise<WebGPUMetaBuffer> {
    const cpuBuffer = WebGPUMetaBuffer.buildCPUBuffer(content);
    const cpuBufferHash = WebGPUMetaBuffer.calcBufferHash(cpuBuffer);
    // 全く同じ内容がプールにあればそれを使い、なければバッファ作成とGPUへの転送
    const found = WebGPUMetaBuffer.findPooled(
      context,
      cpuBuffer,
      cpuBufferHash
    );
    if (found) {
      return found;
    }
    const tensor = new WebGPUTensorImpl(
      context,
      [cpuBuffer.length / 4],
      "float32",
      true,
      false
    );
    await tensor.setData(new Float32Array(cpuBuffer.buffer));
    return new WebGPUMetaBuffer(context, tensor, cpuBuffer, cpuBufferHash);
  }

  pushToPool(): void {
    this.context.pooledMetaBuffer.push(this);
  }
}
