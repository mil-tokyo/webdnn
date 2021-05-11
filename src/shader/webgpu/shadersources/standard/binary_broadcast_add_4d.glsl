#version 450

layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

layout(std430, set = 0, binding = 0) readonly buffer arrayA {
  float numbers[];
} array_a;

layout(std430, set = 0, binding = 1) readonly buffer arrayB {
  float numbers[];
} array_b;

layout(std430, set = 0, binding = 2) buffer arrayC {
  float numbers[];
} array_c;

layout(std430, set = 0, binding = 3) readonly buffer Meta {
  uint len;
  uint outShape0, outShape1, outShape2, outShape3;
  uint inAStride0, inAStride1, inAStride2, inAStride3;
  uint inBStride0, inBStride1, inBStride2, inBStride3;
} meta;

void main() {
  uint len = meta.len;
  uint outShape0 = meta.outShape0, outShape1 = meta.outShape1, outShape2 = meta.outShape2, outShape3 = meta.outShape3;
  uint inAStride0 = meta.inAStride0, inAStride1 = meta.inAStride1, inAStride2 = meta.inAStride2, inAStride3 = meta.inAStride3;
  uint inBStride0 = meta.inBStride0, inBStride1 = meta.inBStride1, inBStride2 = meta.inBStride2, inBStride3 = meta.inBStride3;
  for (uint i = gl_GlobalInvocationID.x; i < len; i += 4096) {
    uint dim3 = i % outShape3;
    uint dim2 = i / outShape3;
    uint dim1 = dim2 / outShape2;
    dim2 = dim2 % outShape2;
    uint dim0 = dim1 / outShape1;
    dim1 = dim1 % outShape1;
    array_c.numbers[i] = array_a.numbers[dim0 * inAStride0 + dim1 * inAStride1 + dim2 * inAStride2 + dim3 * inAStride3] + array_b.numbers[dim0 * inBStride0 + dim1 * inBStride1 + dim2 * inBStride2 + dim3 * inBStride3];
  }
}
