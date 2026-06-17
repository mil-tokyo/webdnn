@group(0) @binding(0) var<storage, read_write> array_a: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_b: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_c: array<f32>;

struct Meta {
  len: u32,
  outShape0: u32,
  outShape1: u32,
  outShape2: u32,
  inAStride0: u32,
  inAStride1: u32,
  inAStride2: u32,
  inBStride0: u32,
  inBStride1: u32,
  inBStride2: u32,
};
@group(0) @binding(3) var<storage, read_write> metaBuf: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let len = metaBuf.len;
  let outShape0 = metaBuf.outShape0;
  let outShape1 = metaBuf.outShape1;
  let outShape2 = metaBuf.outShape2;
  let inAStride0 = metaBuf.inAStride0;
  let inAStride1 = metaBuf.inAStride1;
  let inAStride2 = metaBuf.inAStride2;
  let inBStride0 = metaBuf.inBStride0;
  let inBStride1 = metaBuf.inBStride1;
  let inBStride2 = metaBuf.inBStride2;
  for (var i = global_id.x; i < len; i = i + 4096u) {
    let dim2 = i % outShape2;
    var dim1 = i / outShape2;
    let dim0 = dim1 / outShape1;
    dim1 = dim1 % outShape1;
    array_c[i] = array_a[dim0 * inAStride0 + dim1 * inAStride1 + dim2 * inAStride2] + array_b[dim0 * inBStride0 + dim1 * inBStride1 + dim2 * inBStride2];
  }
}
