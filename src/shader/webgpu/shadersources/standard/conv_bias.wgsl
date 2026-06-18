@group(0) @binding(0) var<storage, read_write> array_i: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_b: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_o: array<f32>;

struct Meta {
  batch: i32,
  chOut: i32,
  outarea: i32,
};
@group(0) @binding(3) var<storage, read_write> metaBuf: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let batch = metaBuf.batch;
  let chOut = metaBuf.chOut;
  let outarea = metaBuf.outarea;
  let total = batch * chOut * outarea;
  for (var idx = i32(global_id.x); idx < total; idx = idx + 4096) {
    let x = idx % outarea;
    var c = idx / outarea;
    // let b = c / chOut;
    c = c % chOut;
    array_o[idx] = array_i[idx] + array_b[c];
  }
}
