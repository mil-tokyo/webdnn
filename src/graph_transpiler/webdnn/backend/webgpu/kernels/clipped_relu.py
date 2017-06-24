from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.graph.operators.clipped_relu import ClippedRelu

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%%[[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = %%LOAD_BUFFER(clipped_relu_X)%%;
    device       float *Y = %%LOAD_BUFFER(clipped_relu_Y)%%;

    const int N = %%LOAD_BUFFER(clipped_relu_N)%%;
    const float cap = *((const device float *)(& %%LOAD_BUFFER(clipped_relu_cap)%%));

    for (int gid = index; gid < N; gid += num_threads) {
        float val = X[gid];

        Y[gid] = val >= 0.0f ? (val < cap ? val : cap) : 0.0f;
    }
}
"""


def clipped_relu(op: ClippedRelu,
                 memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "clipped_relu_X": x,
        "clipped_relu_Y": y,
        "clipped_relu_N": y.variable.size,
        "clipped_relu_cap": op.parameters["cap"]
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
