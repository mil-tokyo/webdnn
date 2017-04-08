#include <metal_stdlib>
using namespace metal;

kernel void warmup(device int *dummy[[buffer(0)]],
                   uint threads[[threads_per_grid]])
{
    for (int i = 0; i < threads - 1; i++)
        dummy[i + 1] = dummy[i];
}