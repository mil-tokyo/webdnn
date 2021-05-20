import { WebDNNCPUContext } from "../../interface/backend/cpu/cpuContext";
import {
  WebDNNWebGPUContext,
  WebGPURunnerRequest,
} from "../../interface/backend/webgpu/webgpuContext";
import { WebGPUTensor } from "../../interface/backend/webgpu/webgpuTensor";
import { DataType } from "../../interface/core/constants";
import { Tensor } from "../../interface/core/tensor";
import { WebGPUMetaBuffer } from "./webgpuMetaBuffer";
import { WebGPUTensorImpl } from "./webgpuTensorImpl";

interface WebGPURunnerPipeline {
  bindGroupLayout: GPUBindGroupLayout;
  pipeline: GPUComputePipeline;
}

export class WebDNNWebGPUContextImpl implements WebDNNWebGPUContext {
  backend = "webgpu" as const;

  initialized: boolean;

  isSupported: boolean;

  device!: GPUDevice;

  private pipelines: Map<string, WebGPURunnerPipeline>;

  pooledMetaBuffer: WebGPUMetaBuffer[] = [];

  constructor(public cpuContext: WebDNNCPUContext) {
    if (
      typeof navigator.gpu !== "object" ||
      typeof navigator.gpu.requestAdapter !== "function"
    ) {
      throw new Error("WebGPU is not supported on this browser");
    }
    this.initialized = false;
    this.isSupported = false;
    this.pipelines = new Map();
  }

  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    const adapter = await navigator.gpu!.requestAdapter();
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    this.device = (await adapter!.requestDevice()) as GPUDevice;
    if (!this.device) {
      throw new Error("GPUAdapter.requestDevice() returned null");
    }
    this.isSupported = true;
    this.initialized = true;
  }

  isWebGLTensor(tensor: Tensor): tensor is WebGPUTensor {
    return tensor.backend === this.backend;
  }

  assertsWebGPUTensor(tensor: Tensor): asserts tensor is WebGPUTensor {
    if (tensor.backend !== this.backend) {
      throw new Error(
        `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
      );
    }
  }

  assertsWebGPUTensorArray(
    tensors: Tensor[]
  ): asserts tensors is WebGPUTensor[] {
    for (const tensor of tensors) {
      if (tensor.backend !== this.backend) {
        throw new Error(
          `Tensor backend ${this.backend} is expected, but ${tensor.backend} is given.`
        );
      }
    }
  }

  emptyTensor(
    dims: ReadonlyArray<number>,
    dataType?: DataType,
    forWriteFromCPU?: boolean,
    forReadToCPU?: boolean
  ): WebGPUTensor {
    return new WebGPUTensorImpl(
      this,
      dims,
      dataType,
      forWriteFromCPU,
      forReadToCPU
    );
  }

  async moveTensor(tensor: Tensor): Promise<WebGPUTensor> {
    const dst = new WebGPUTensorImpl(
      this,
      tensor.dims,
      tensor.dataType,
      true,
      false
    );
    await dst.setData(await tensor.getData());
    return dst;
  }

  hasPipeline(name: string): boolean {
    return this.pipelines.has(name);
  }

  createPipeline(name: string, shader: Uint32Array, nBuffers: number): void {
    if (this.hasPipeline(name)) {
      return;
    }
    const { device } = this,
      bindings: GPUBindGroupLayoutEntry[] = [];
    for (let i = 0; i < nBuffers; i++) {
      bindings.push({
        binding: i,
        visibility: GPUShaderStage.COMPUTE,
        buffer: { type: "storage" },
      });
    }
    const bindGroupLayout = device.createBindGroupLayout({
        entries: bindings,
      }),
      pipelineLayout = device.createPipelineLayout({
        bindGroupLayouts: [bindGroupLayout],
      }),
      shaderModule = device.createShaderModule({ code: shader }),
      pipeline = device.createComputePipeline({
        layout: pipelineLayout,
        computeStage: {
          module: shaderModule,
          entryPoint: "main",
        },
      });

    this.pipelines.set(name, { bindGroupLayout, pipeline });
  }

  async run(request: WebGPURunnerRequest): Promise<void> {
    const pipeline = this.pipelines.get(request.pipelineName);
    if (!pipeline) {
      throw new Error(`Pipeline ${pipeline} not found`);
    }
    const { device } = this,
      entries: GPUBindGroupEntry[] = request.tensors.map((t, i) => ({
        binding: i,
        resource: {
          buffer: (t as WebGPUTensorImpl).buffer,
          size: (t as WebGPUTensorImpl).bufferSize,
        },
      }));
    let meta: WebGPUMetaBuffer | null = null;
    if (request.meta) {
      meta = await WebGPUMetaBuffer.createBuffer(this, request.meta);
      entries.push({
        binding: entries.length,
        resource: {
          buffer: meta.tensor.buffer,
          size: meta.tensor.bufferSize,
        },
      });
    }
    const bindGroup = device.createBindGroup({
        layout: pipeline.bindGroupLayout,
        entries,
      }),
      commandEncoder = device.createCommandEncoder(),
      passEncoder = commandEncoder.beginComputePass();
    passEncoder.setBindGroup(0, bindGroup);
    passEncoder.setPipeline(pipeline.pipeline);
    passEncoder.dispatch(
      request.workGroups.x,
      request.workGroups.y,
      request.workGroups.z
    );
    passEncoder.endPass();

    device.queue.submit([commandEncoder.finish()]);

    meta?.pushToPool();
  }
}
