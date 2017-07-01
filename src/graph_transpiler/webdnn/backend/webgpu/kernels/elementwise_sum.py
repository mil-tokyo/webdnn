from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.inline_injector import InlineInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.axiswise_scale import AxiswiseScale


def generate_template(N, has_inline):
    return """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
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
    const device float4 *X0 = (const device float4 *)(%%LOAD_BUFFER(elementwise_sum_X0)%%);
    const device float4 *X1 = (const device float4 *)(%%LOAD_BUFFER(elementwise_sum_X1)%%);
    device float4 *Y = (device float4 *)(%%LOAD_BUFFER(elementwise_sum_Y)%%);
    const int N = (%%LOAD_BUFFER(elementwise_sum_N)%%) >> 2;
#else
    const device float *X0 = %%LOAD_BUFFER(elementwise_sum_X0)%%;
    const device float *X1 = %%LOAD_BUFFER(elementwise_sum_X1)%%;
    device float *Y = %%LOAD_BUFFER(elementwise_sum_Y)%%;
    const int N = %%LOAD_BUFFER(elementwise_sum_N)%%;
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

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "elementwise_sum_X0": x0,
        "elementwise_sum_X1": x1,
        "elementwise_sum_Y": y,
        "elementwise_sum_N": y.variable.size
    })

    inline_injector = InlineInjector(op)
    name_injector = KernelNameInjector(op)

    source = generate_template(y.variable.size, inline_injector.has_inline)
    source = buffer_injector.inject(source)
    source = inline_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(MAX_THREADS_PER_THREADGROUP, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
