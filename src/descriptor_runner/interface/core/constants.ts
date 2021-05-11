export type Backend = "cpu" | "webgl" | "wasm" | "webgpu";
export type DataType = "float32" | "int32" | "bool";
export const DataArrayConstructor = {
  float32: Float32Array,
  int32: Int32Array,
  bool: Uint8Array,
};
export type DataArrayTypes = Float32Array | Int32Array | Uint8Array;
