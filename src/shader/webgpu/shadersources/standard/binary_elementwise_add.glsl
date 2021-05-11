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
} meta;

void main() {
  uint len = meta.len;
  for (uint i = gl_GlobalInvocationID.x; i < len; i += 4096) {
    array_c.numbers[i] = array_a.numbers[i] + array_b.numbers[i];
  }
}
