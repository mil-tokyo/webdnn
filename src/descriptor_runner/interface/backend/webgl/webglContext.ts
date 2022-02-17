import { BackendContext } from "../../core/backendContext";
import { DataType } from "../../core/constants";
import { Tensor } from "../../core/tensor";
import { WebDNNCPUContext } from "../cpu/cpuContext";
import { WebGLTensor } from "./webglTensor";

export interface WebGLUniformItem {
  name: string;
  value: number;
  type: "float" | "int";
}

export type WebDNNWebGLVersion =
  | "webgl2-16384"
  | "webgl2-4096"
  | "webgl1-16384"
  | "webgl1-4096";

export interface WebDNNWebGLContextOption {
  /**
   * Version order in which initialization is attempted.
   * The version means the combination of webgl version and max texture size.
   */
  versionOrder?: WebDNNWebGLVersion[];
  /**
   * Maximum GPU memory allocation in the context.
   * Pool deleted textures for future use until this capacity is exceeded.
   */
  maxAllocationBytes?: number;
  /**
   * When memory deletion is needed, the deallocation occurs until total memory allocation becomes below this value.
   */
  deallocateToBytes?: number;
}

export interface WebDNNWebGLContextPerformance {
  key: string;
  kernelName: string;
  inputs: { name: string; dims: number[] }[];
  output: { dims: number[] };
  elapsedNanoSecond: number;
  gpuDisjoint: boolean;
}

export interface WebDNNWebGLContext extends BackendContext {
  backend: "webgl";
  cpuContext: WebDNNCPUContext;
  canOnlyReadRGBA: boolean;
  gl: WebGLRenderingContext | WebGL2RenderingContext;
  webgl2: boolean;
  maxTextureSize: number;
  version: WebDNNWebGLVersion;

  initialize(): Promise<void>;
  isWebGLTensor(tensor: Tensor): tensor is WebGLTensor;
  assertsWebGLTensor(tensor: Tensor): asserts tensor is WebGLTensor;
  assertsWebGLTensorArray(tensors: Tensor[]): asserts tensors is WebGLTensor[];
  emptyTensor(
    dims: ReadonlyArray<number>,
    dataType?: DataType,
    option?: { dimPerPixel?: 1 | 4; textureShape?: ReadonlyArray<number> }
  ): WebGLTensor;
  moveTensor(
    tensor: Tensor,
    option: { dimPerPixel?: 1 | 4; textureShape?: ReadonlyArray<number> }
  ): Promise<WebGLTensor>;
  addKernel(name: string, sourceCode: string): void;
  hasKernel(name: string): boolean;
  runKernel(
    name: string,
    inputs: { tensor: WebGLTensor; name: string }[],
    output: WebGLTensor,
    uniforms: WebGLUniformItem[]
  ): Promise<void>;
  enablePerformanceQuery(key: string | null): void;
  gatherPerformanceQueryResult(): Promise<WebDNNWebGLContextPerformance[]>;
}
