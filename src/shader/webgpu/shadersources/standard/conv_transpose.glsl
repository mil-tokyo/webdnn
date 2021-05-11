#version 450

layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

layout(std430, set = 0, binding = 0) readonly buffer arrayT {
  float numbers[];
} array_t;

layout(std430, set = 0, binding = 1) buffer arrayO {
  float numbers[];
} array_o;

layout(std430, set = 0, binding = 2) readonly buffer arrayMeta {
  int group, batch, outarea, chOutPerGroup;
} meta;

void main() {
  int group = meta.group, batch = meta.batch, outarea = meta.outarea, chOutPerGroup = meta.chOutPerGroup;
  int total = group * batch * chOutPerGroup * outarea;
  for (int idx = int(gl_GlobalInvocationID.x); idx < total; idx += 4096) {
    int x = idx % outarea;
    int c = idx / outarea;
    int g = c / chOutPerGroup;
    c = c % chOutPerGroup;
    int b = g / group;
    g = g % group;
    array_o.numbers[idx] = array_t.numbers[((g * batch + b) * outarea + x) * chOutPerGroup + c];
  }
}
