import { BackendContext } from "../../core/backendContext";
import { DataType } from "../../core/constants";
import { Tensor } from "../../core/tensor";
import { WebDNNCPUContext } from "../cpu/cpuContext";
import { WebGPUTensor } from "./webgpuTensor";

type WorkGroupDim = "x" | "y" | "z";

export interface WebGPUMetaBufferContentElement {
  value: number;
  type: "int32" | "uint32" | "float32";
}

export interface WebGPUMetaBufferContent {
  elements: WebGPUMetaBufferContentElement[];
}

export interface WebGPURunnerRequest {
  pipelineName: string;
  tensors: WebGPUTensor[];
  meta: WebGPUMetaBufferContent | null;
  workGroups: { [key in WorkGroupDim]: number };
}

export interface WebDNNWebGPUContext extends BackendContext {
  backend: "webgpu";
  cpuContext: WebDNNCPUContext;
  initialize(): Promise<void>;
  isWebGLTensor(tensor: Tensor): tensor is WebGPUTensor;
  assertsWebGPUTensor(tensor: Tensor): asserts tensor is WebGPUTensor;
  assertsWebGPUTensorArray(
    tensors: Tensor[]
  ): asserts tensors is WebGPUTensor[];

  emptyTensor(
    dims: ReadonlyArray<number>,
    dataType?: DataType,
    forWriteFromCPU?: boolean,
    forReadToCPU?: boolean
  ): WebGPUTensor;
  // eslint-disable-next-line @typescript-eslint/ban-types
  moveTensor(tensor: Tensor, option: {}): Promise<WebGPUTensor>;
  hasPipeline(name: string): boolean;
  createPipeline(name: string, shader: Uint32Array, nBuffers: number): void;
  run(request: WebGPURunnerRequest): Promise<void>;
}
