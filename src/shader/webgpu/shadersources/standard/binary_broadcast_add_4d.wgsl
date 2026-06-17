@group(0) @binding(0) var<storage, read_write> array_a: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_b: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_c: array<f32>;

struct Meta {
  len: u32,
  outShape0: u32,
  outShape1: u32,
  outShape2: u32,
  outShape3: u32,
  inAStride0: u32,
  inAStride1: u32,
  inAStride2: u32,
  inAStride3: u32,
  inBStride0: u32,
  inBStride1: u32,
  inBStride2: u32,
  inBStride3: u32,
};
@group(0) @binding(3) var<storage, read_write> meta: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let len = meta.len;
  let outShape0 = meta.outShape0;
  let outShape1 = meta.outShape1;
  let outShape2 = meta.outShape2;
  let outShape3 = meta.outShape3;
  let inAStride0 = meta.inAStride0;
  let inAStride1 = meta.inAStride1;
  let inAStride2 = meta.inAStride2;
  let inAStride3 = meta.inAStride3;
  let inBStride0 = meta.inBStride0;
  let inBStride1 = meta.inBStride1;
  let inBStride2 = meta.inBStride2;
  let inBStride3 = meta.inBStride3;
  for (var i = global_id.x; i < len; i = i + 4096u) {
    let dim3 = i % outShape3;
    var dim2 = i / outShape3;
    var dim1 = dim2 / outShape2;
    dim2 = dim2 % outShape2;
    let dim0 = dim1 / outShape1;
    dim1 = dim1 % outShape1;
    array_c[i] = array_a[dim0 * inAStride0 + dim1 * inAStride1 + dim2 * inAStride2 + dim3 * inAStride3] + array_b[dim0 * inBStride0 + dim1 * inBStride1 + dim2 * inBStride2 + dim3 * inBStride3];
  }
}
