#version 450

layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;

layout(std430, set = 0, binding = 0) readonly buffer arrayI {
  float numbers[];
} array_i;

layout(std430, set = 0, binding = 1) readonly buffer arrayB {
  float numbers[];
} array_b;

layout(std430, set = 0, binding = 2) buffer arrayO {
  float numbers[];
} array_o;

layout(std430, set = 0, binding = 3) readonly buffer arrayMeta {
  int batch, chOut, outarea;
} meta;

void main() {
  int batch = meta.batch, chOut = meta.chOut, outarea = meta.outarea;
  int total = batch * chOut * outarea;
  for (int idx = int(gl_GlobalInvocationID.x); idx < total; idx += 4096) {
    int x = idx % outarea;
    int c = idx / outarea;
    // int b = c / chOut;
    c = c % chOut;
    array_o.numbers[idx] = array_i.numbers[idx] + array_b.numbers[c];
  }
}
