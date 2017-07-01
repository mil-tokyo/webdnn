from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.scalar_affine import ScalarAffine

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = %%LOAD_BUFFER(affine_transform_X)%%;
    device float *Y = %%LOAD_BUFFER(affine_transform_Y)%%;

    const float scale = *((const device float *)(& %%LOAD_BUFFER(affine_transform_scale)%%));
    const float bias = *((const device float *)(& %%LOAD_BUFFER(affine_transform_bias)%%));
    const int N = %%LOAD_BUFFER(affine_transform_N)%%;

    for (int gid = index; gid < N; gid += num_threads) {
        float result = X[gid];
        result = result * scale + bias;
        
        Y[gid] = result;
    }
}
"""


def scalar_affine(op: ScalarAffine,
                  memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]
    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "affine_transform_X": x,
        "affine_transform_Y": y,
        "affine_transform_N": y.variable.size,
        "affine_transform_scale": float(op.scale),
        "affine_transform_bias": float(op.bias)
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
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
