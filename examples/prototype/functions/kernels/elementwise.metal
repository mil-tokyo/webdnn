#include <metal_stdlib>
using namespace metal;

kernel void relu_inplace(const device int *_n[[buffer(0)]],
                         device float *x[[buffer(1)]],
                         uint gid[[thread_position_in_grid]],
                         uint num_threads[[threads_per_grid]])
{
    if (gid >= _n[0])
        return;

    x[gid] = x[gid] > 0 ? x[gid] : 0;
}

kernel void bn_fixed_inplace(const device int *_n[[buffer(0)]],
                             device float *x[[buffer(1)]],
                             uint gid[[thread_position_in_grid]],
                             uint num_threads[[threads_per_grid]])
{
    //FIXME:
    const float sigma = 1.0;
    const float beta = 0.1;

    if (gid >= _n[0])
        return;

    x[gid] = x[gid] * sigma + beta;
}

kernel void relu_and_bn_fixed_inplace(const device int *_n[[buffer(0)]],
                                      device float *x[[buffer(1)]],
                                      uint gid[[thread_position_in_grid]],
                                      uint num_threads[[threads_per_grid]])
{
    //FIXME:
    const float sigma = 1.0;
    const float beta = 0.1;

    if (gid >= _n[0])
        return;

    x[gid] = (x[gid] > 0 ? x[gid] : 0) * sigma + beta;
}
