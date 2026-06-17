@group(0) @binding(0) var<storage, read_write> array_a: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_b: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_c: array<f32>;

struct Meta {
  len: u32,
  outShape0: u32,
  outShape1: u32,
  inAStride0: u32,
  inAStride1: u32,
  inBStride0: u32,
  inBStride1: u32,
};
@group(0) @binding(3) var<storage, read_write> meta: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let len = meta.len;
  let outShape0 = meta.outShape0;
  let outShape1 = meta.outShape1;
  let inAStride0 = meta.inAStride0;
  let inAStride1 = meta.inAStride1;
  let inBStride0 = meta.inBStride0;
  let inBStride1 = meta.inBStride1;
  for (var i = global_id.x; i < len; i = i + 4096u) {
    let dim1 = i % outShape1;
    let dim0 = i / outShape1;
    array_c[i] = array_a[dim0 * inAStride0 + dim1 * inAStride1] + array_b[dim0 * inBStride0 + dim1 * inBStride1];
  }
}
