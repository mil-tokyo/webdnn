from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.inline_injector import InlineInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.operators.axiswise_scale import AxiswiseScale


def generate_template(N, has_inline):
    return """
kernel void %%FUNC_NAME%%(device float *data_buffer[[buffer(0)]],
                          const device int * %%META_NAME%% [[buffer(1)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
#define N_DIVIDABLE_BY_4 %%N_DIVIDABLE_BY_4%%
#define HAS_INLINE %%HAS_INLINE%%

#if OPTIMIZE && N_DIVIDABLE_BY_4
    #define T_VALUE float4
#else
    #define T_VALUE float
#endif


#if OPTIMIZE && N_DIVIDABLE_BY_4
    const device float4 *X0 = (const device float4 *)(data_buffer + %%META_LOAD(elementwise_sum_X0_offset)%%);
    const device float4 *X1 = (const device float4 *)(data_buffer + %%META_LOAD(elementwise_sum_X1_offset)%%);
    device float4 *Y = (device float4 *)(data_buffer + %%META_LOAD(elementwise_sum_Y_offset)%%);
    const int N = (%%META_LOAD(elementwise_sum_N)%%) >> 2;
#else
    const device float *X0 = data_buffer + %%META_LOAD(elementwise_sum_X0_offset)%%;
    const device float *X1 = data_buffer + %%META_LOAD(elementwise_sum_X1_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(elementwise_sum_Y_offset)%%;
    const int N = %%META_LOAD(elementwise_sum_N)%%;
#endif
  
    for (int gid = index; gid < N; gid += num_threads) {

        T_VALUE result = X0[gid] + X1[gid];

#if OPTIMIZE && HAS_INLINE
    #if OPTIMIZE && N_DIVIDABLE_BY_4
            result[0] = %%INLINE(result[0])%%;
            result[1] = %%INLINE(result[1])%%;
            result[2] = %%INLINE(result[2])%%;
            result[3] = %%INLINE(result[3])%%;
    #else
            result = %%INLINE(result)%%;
    #endif
#endif

        Y[gid] = result;
    }


#undef N_DIVIDABLE_BY_4 
#undef HAS_INLINE
}
""" \
        .replace("%%N_DIVIDABLE_BY_4%%", "1" if N % 4 == 0 else "0") \
        .replace("%%HAS_INLINE%%", "1" if has_inline else "0")


def elementwise_sum(op: AxiswiseScale,
                    memory_layout: MemoryLayout) -> List[Kernel]:
    x0 = memory_layout[op.inputs["x0"]]
    x1 = memory_layout[op.inputs["x1"]]
    y = memory_layout[op.outputs["y"]]

    assert len(op.inputs) == 2, "[WebGPU] ElementwiseSum operator currently supported only 2 inputs."
    assert x0.variable.shape == x1.variable.shape == y.variable.shape

    meta_injector = MetaInjector()
    meta_injector.register({
        "elementwise_sum_X0_offset": x0.offset,
        "elementwise_sum_X1_offset": x1.offset,
        "elementwise_sum_Y_offset": y.offset,
        "elementwise_sum_N": y.variable.size
    })

    inline_injector = InlineInjector(op)
    name_injector = KernelNameInjector(op)

    source = generate_template(y.variable.size, inline_injector.has_inline)
    source = meta_injector.inject(source)
    source = inline_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        meta_injector.buffer
    )

    return [kernel]
