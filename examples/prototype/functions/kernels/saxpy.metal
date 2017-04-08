#include <metal_stdlib>
using namespace metal;

kernel void saxpy(const device int *_n[[buffer(0)]],
                  const device float *_a[[buffer(1)]],
                  const device float *x[[buffer(2)]],
                  device float *y[[buffer(3)]],
                  uint index[[thread_position_in_grid]],
                  uint num_threads[[threads_per_grid]])
{
    const int n = _n[0];
    const float a = _a[0];
    for (int gid = index; gid < N; gid += num_threads)
        y[gid] += a * x[gid];
}
