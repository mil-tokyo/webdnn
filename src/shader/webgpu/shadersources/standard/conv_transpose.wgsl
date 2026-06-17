@group(0) @binding(0) var<storage, read_write> array_t: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_o: array<f32>;

struct Meta {
  group: i32,
  batch: i32,
  outarea: i32,
  chOutPerGroup: i32,
};
@group(0) @binding(2) var<storage, read_write> meta: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let group = meta.group;
  let batch = meta.batch;
  let outarea = meta.outarea;
  let chOutPerGroup = meta.chOutPerGroup;
  let total = group * batch * chOutPerGroup * outarea;
  for (var idx = i32(global_id.x); idx < total; idx = idx + 4096) {
    let x = idx % outarea;
    var c = idx / outarea;
    var g = c / chOutPerGroup;
    c = c % chOutPerGroup;
    let b = g / group;
    g = g % group;
    array_o[idx] = array_t[((g * batch + b) * outarea + x) * chOutPerGroup + c];
  }
}
