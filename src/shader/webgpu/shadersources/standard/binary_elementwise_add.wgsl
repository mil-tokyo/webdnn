@group(0) @binding(0) var<storage, read_write> array_a: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_b: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_c: array<f32>;

struct Meta {
  len: u32,
};
@group(0) @binding(3) var<storage, read_write> metaBuf: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let len = metaBuf.len;
  for (var i = global_id.x; i < len; i = i + 4096u) {
    array_c[i] = array_a[i] + array_b[i];
  }
}
