#version 450

layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

layout(std430, set = 0, binding = 0) readonly buffer arrayI {
  float numbers[];
} array_i;

layout(std430, set = 0, binding = 1) readonly buffer arrayW {
  float numbers[];
} array_w;

layout(std430, set = 0, binding = 2) buffer arrayT {
  float numbers[];
} array_t;

layout(std430, set = 0, binding = 3) readonly buffer arrayMeta {
  int group, bout, chOutPerGroup, cinkhkw;
} meta;

void main() {
  int group = meta.group, bout = meta.bout, chOutPerGroup = meta.chOutPerGroup, cinkhkw = meta.cinkhkw;
  int total = group * bout * chOutPerGroup;
  for (int idx = int(gl_GlobalInvocationID.x); idx < total; idx += 4096) {
    int x = idx % chOutPerGroup;
    int y = idx / chOutPerGroup;
    int g = y / bout;
    y = y % bout;
    float s = 0.0;
    for (int ip = 0; ip < cinkhkw; ip++) {
      s += array_i.numbers[(g * bout + y) * cinkhkw + ip] * array_w.numbers[(g * chOutPerGroup + x) * cinkhkw + ip];
    }
    array_t.numbers[idx] = s;
  }
}
