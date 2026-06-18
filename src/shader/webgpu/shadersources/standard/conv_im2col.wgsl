@group(0) @binding(0) var<storage, read_write> array_x: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_y: array<f32>;

struct Meta {
  group: i32,
  batch: i32,
  outShape0: i32,
  outShape1: i32,
  chInPerGroup: i32,
  kernelShape0: i32,
  kernelShape1: i32,
  strides0: i32,
  strides1: i32,
  pads0: i32,
  pads1: i32,
  dilations0: i32,
  dilations1: i32,
  inShape0: i32,
  inShape1: i32,
  chIn: i32,
};
@group(0) @binding(2) var<storage, read_write> metaBuf: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let group = metaBuf.group;
  let batch = metaBuf.batch;
  let outShape0 = metaBuf.outShape0;
  let outShape1 = metaBuf.outShape1;
  let chInPerGroup = metaBuf.chInPerGroup;
  let kernelShape0 = metaBuf.kernelShape0;
  let kernelShape1 = metaBuf.kernelShape1;
  let strides0 = metaBuf.strides0;
  let strides1 = metaBuf.strides1;
  let pads0 = metaBuf.pads0;
  let pads1 = metaBuf.pads1;
  let dilations0 = metaBuf.dilations0;
  let dilations1 = metaBuf.dilations1;
  let inShape0 = metaBuf.inShape0;
  let inShape1 = metaBuf.inShape1;
  let chIn = metaBuf.chIn;
  let total = group * batch * outShape0 * outShape1 * chInPerGroup * kernelShape0 * kernelShape1;
  for (var idx = i32(global_id.x); idx < total; idx = idx + 4096) {
    var ky = idx / kernelShape1;
    let kx = idx % kernelShape1;
    var ci = ky / kernelShape0;
    ky = ky % kernelShape0;
    var ox = ci / chInPerGroup;
    ci = ci % chInPerGroup;
    var oy = ox / outShape1;
    ox = ox % outShape1;
    var b = oy / outShape0;
    oy = oy % outShape0;
    var g = b / batch;
    b = b % batch;

    let iny = oy * strides0 - pads0 + ky * dilations0;
    let inx = ox * strides1 - pads1 + kx * dilations1;
    var v: f32;
    if (iny >= 0 && iny < inShape0 && inx >= 0 && inx < inShape1) {
      v = array_x[u32(((b * chIn + g * chInPerGroup + ci) * inShape0 + iny) * inShape1 + inx)];
    } else {
      v = 0.0;
    }
    array_y[idx] = v;
  }
}
