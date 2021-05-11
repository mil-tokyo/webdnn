#version 450

layout(local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

layout(std430, set = 0, binding = 0) readonly buffer arrayA {
  float numbers[];
} array_a;

layout(std430, set = 0, binding = 1) readonly buffer arrayB {
  float numbers[];
} array_b;

layout(std430, set = 0, binding = 2) readonly buffer arrayC {
  float numbers[];
} array_c;

layout(std430, set = 0, binding = 3) buffer arrayY {
  float numbers[];
} array_y;

layout(std430, set = 0, binding = 4) readonly buffer arrayMeta {
  uint M;
  uint N;
  uint K;
  uint strideA0, strideA1;
  uint strideB0, strideB1;
  uint strideC0, strideC1;
  float alpha;
  float beta;
} meta;

void main() {
  uint M = meta.M, N = meta.N, K = meta.K;
  uint strideA0 = meta.strideA0, strideA1 = meta.strideA1, strideB0 = meta.strideB0, strideB1 = meta.strideB1, strideC0 = meta.strideC0, strideC1 = meta.strideC1;
  float alpha = meta.alpha, beta = meta.beta;
  for (uint x = uint(gl_GlobalInvocationID.x); x < N; x+=256) {
    for (uint y = uint(gl_GlobalInvocationID.y); y < M; y+=256) {
      float sum = 0.0;
      for(uint k=0;k<K;k++) {
        sum += array_a.numbers[y * strideA0 + k * strideA1] * array_b.numbers[k * strideB0 + x * strideB1];
      }
      array_y.numbers[x + y * N] = sum * alpha + array_c.numbers[y * strideC0 + x * strideC1] * beta;
    }
  }
}
