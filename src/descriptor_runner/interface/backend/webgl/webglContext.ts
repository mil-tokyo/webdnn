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

export interface WebDNNWebGLContext extends BackendContext {
  backend: "webgl";
  cpuContext: WebDNNCPUContext;
  canOnlyReadRGBA: boolean;
  gl: WebGLRenderingContext | WebGL2RenderingContext;
  webgl2: boolean;

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
}
