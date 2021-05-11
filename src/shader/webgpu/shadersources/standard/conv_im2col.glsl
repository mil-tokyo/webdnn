#version 450

layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

layout(std430, set = 0, binding = 0) readonly buffer arrayX {
  float numbers[];
} array_x;

layout(std430, set = 0, binding = 1) buffer arrayY {
  float numbers[];
} array_y;

layout(std430, set = 0, binding = 2) readonly buffer arrayMeta {
  int group, batch, outShape0, outShape1, chInPerGroup, kernelShape0, kernelShape1;
  int strides0, strides1, pads0, pads1, dilations0, dilations1;
  int inShape0, inShape1;
  int chIn;
} meta;

void main() {
  int group = meta.group, batch = meta.batch, outShape0 = meta.outShape0, outShape1 = meta.outShape1, chInPerGroup = meta.chInPerGroup, kernelShape0 = meta.kernelShape0, kernelShape1 = meta.kernelShape1;
  int strides0 = meta.strides0, strides1 = meta.strides1, pads0 = meta.pads0, pads1 = meta.pads1, dilations0 = meta.dilations0, dilations1 = meta.dilations1;
  int inShape0 = meta.inShape0, inShape1 = meta.inShape1;
  int chIn = meta.chIn;
  int total = group * batch * outShape0 * outShape1 * chInPerGroup * kernelShape0 * kernelShape1;
  for (int idx = int(gl_GlobalInvocationID.x); idx < total; idx += 4096) {
    int ky = idx / kernelShape1;
    int kx = idx % kernelShape1;
    int ci = ky / kernelShape0;
    ky = ky % kernelShape0;
    int ox = ci / chInPerGroup;
    ci = ci % chInPerGroup;
    int oy = ox / outShape1;
    ox = ox % outShape1;
    int b = oy / outShape0;
    oy = oy % outShape0;
    int g = b / batch;
    b = b % batch;

    int iny = oy * strides0 - pads0 + ky * dilations0;
    int inx = ox * strides1 - pads1 + kx * dilations1;
    float v;
    if (iny >= 0 && iny < inShape0 && inx >= 0 && inx < inShape1) {
      v = array_x.numbers[((b * chIn + g * chInPerGroup + ci) * inShape0 + iny) * inShape1 + inx];
    } else {
      v = 0.0;
    }
    array_y.numbers[idx] = v;
  }
}
