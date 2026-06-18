@group(0) @binding(0) var<storage, read_write> array_a: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_b: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_c: array<f32>;
@group(0) @binding(3) var<storage, read_write> array_y: array<f32>;

struct Meta {
  M: u32,
  N: u32,
  K: u32,
  strideA0: u32,
  strideA1: u32,
  strideB0: u32,
  strideB1: u32,
  strideC0: u32,
  strideC1: u32,
  alpha: f32,
  beta: f32,
};
@group(0) @binding(4) var<storage, read_write> metaBuf: Meta;

@compute @workgroup_size(8, 8, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let M = metaBuf.M;
  let N = metaBuf.N;
  let K = metaBuf.K;
  let strideA0 = metaBuf.strideA0;
  let strideA1 = metaBuf.strideA1;
  let strideB0 = metaBuf.strideB0;
  let strideB1 = metaBuf.strideB1;
  let strideC0 = metaBuf.strideC0;
  let strideC1 = metaBuf.strideC1;
  let alpha = metaBuf.alpha;
  let beta = metaBuf.beta;
  for (var x = global_id.x; x < N; x = x + 256u) {
    for (var y = global_id.y; y < M; y = y + 256u) {
      var sum = 0.0;
      for (var k = 0u; k < K; k = k + 1u) {
        sum = sum + array_a[y * strideA0 + k * strideA1] * array_b[k * strideB0 + x * strideB1];
      }
      array_y[x + y * N] = sum * alpha + array_c[y * strideC0 + x * strideC1] * beta;
    }
  }
}
