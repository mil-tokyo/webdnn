@group(0) @binding(0) var<storage, read_write> array_i: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_w: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_t: array<f32>;

struct Meta {
  group: i32,
  bout: i32,
  chOutPerGroup: i32,
  cinkhkw: i32,
};
@group(0) @binding(3) var<storage, read_write> metaBuf: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let group = metaBuf.group;
  let bout = metaBuf.bout;
  let chOutPerGroup = metaBuf.chOutPerGroup;
  let cinkhkw = metaBuf.cinkhkw;
  let total = group * bout * chOutPerGroup;
  for (var idx = i32(global_id.x); idx < total; idx = idx + 4096) {
    let x = idx % chOutPerGroup;
    var y = idx / chOutPerGroup;
    let g = y / bout;
    y = y % bout;
    var s = 0.0;
    for (var ip = 0; ip < cinkhkw; ip = ip + 1) {
      s = s + array_i[(g * bout + y) * cinkhkw + ip] * array_w[(g * chOutPerGroup + x) * cinkhkw + ip];
    }
    array_t[idx] = s;
  }
}
