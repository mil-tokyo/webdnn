from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.sum import Sum

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = %%LOAD_BUFFER(sum_X)%%;
    device float *Y = %%LOAD_BUFFER(sum_Y)%%;
    const device int *y_stride = %%LOAD_BUFFER(sum_y_stride)%%;
    const device int *y_shape = %%LOAD_BUFFER(sum_y_shape)%%;
    const device int *x_stride = %%LOAD_BUFFER(sum_x_stride)%%;
    const int D = %%LOAD_BUFFER(sum_D)%%;
    const int N = %%LOAD_BUFFER(sum_N)%%;
    const int MAX_GID = %%LOAD_BUFFER(sum_MAX_GID)%%;
    const int x_target_axis_stride = %%LOAD_BUFFER(sum_x_target_axis_stride)%%;

    for (int gid = index; gid < MAX_GID; gid += num_threads) {
        int x_index = 0;
        for (int d = 0; d < D; d++) x_index += ((gid / y_stride[d]) % y_shape[d]) * x_stride[d];

        float y = 0.0f;
        for (int i = 0; i < N; i++) {
            const float x = X[x_index];

            y += x;

            x_index += x_target_axis_stride;
        }

        Y[gid] = y;
    }
}
"""


@WebGPUDescriptorGenerator.register_handler(Sum)
def sum_handler(op: Sum, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    axis = op.parameters["axis"]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "sum_X": memory_layout[x],
        "sum_Y": memory_layout[y],
        "sum_y_stride": y.stride,
        "sum_y_shape": y.shape,
        "sum_x_stride": [x.stride_dict[a] for a in y.order.axes],
        "sum_D": y.ndim,
        "sum_N": x.shape_dict[axis],
        "sum_MAX_GID": y.size,
        "sum_x_target_axis_stride": x.stride_dict[axis]
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
