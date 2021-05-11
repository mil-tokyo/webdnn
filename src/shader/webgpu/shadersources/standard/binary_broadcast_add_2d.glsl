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
  uint outShape0, outShape1;
  uint inAStride0, inAStride1;
  uint inBStride0, inBStride1;
} meta;

void main() {
  uint len = meta.len;
  uint outShape0 = meta.outShape0, outShape1 = meta.outShape1;
  uint inAStride0 = meta.inAStride0, inAStride1 = meta.inAStride1;
  uint inBStride0 = meta.inBStride0, inBStride1 = meta.inBStride1;
  for (uint i = gl_GlobalInvocationID.x; i < len; i += 4096) {
    uint dim1 = i % outShape1;
    uint dim0 = i / outShape1;
    array_c.numbers[i] = array_a.numbers[dim0 * inAStride0 + dim1 * inAStride1] + array_b.numbers[dim0 * inBStride0 + dim1 * inBStride1];
  }
}
