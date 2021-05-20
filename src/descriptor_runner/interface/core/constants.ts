export type BackendWithoutCPU = "webgl" | "wasm" | "webgpu";
export type Backend = "cpu" | BackendWithoutCPU;
export const backendsWithoutCPU: BackendWithoutCPU[] = [
  "wasm",
  "webgl",
  "webgpu",
];
export const backends: Backend[] = ["cpu", "wasm", "webgl", "webgpu"];
export type DataType = "float32" | "int32" | "bool";
export const DataArrayConstructor = {
  float32: Float32Array,
  int32: Int32Array,
  bool: Uint8Array,
};
export type DataArrayTypes = Float32Array | Int32Array | Uint8Array;
