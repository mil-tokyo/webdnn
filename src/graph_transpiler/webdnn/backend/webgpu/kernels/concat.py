from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.concat import Concat

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    device float *y = %%LOAD_BUFFER(concat_y)%%;
    const char N = %%LOAD_BUFFER(concat_N)%%;
    const char D = %%LOAD_BUFFER(concat_D)%%;
    const device int *y_offsets = %%LOAD_BUFFER(concat_y_offsets)%%;
    const device int *x_shapes = %%LOAD_BUFFER(concat_x_shapes)%%;
    const device int *x_strides_in_y = %%LOAD_BUFFER(concat_x_strides_in_y)%%;

    int x_index = index;

    for (int n = 0; n < N; n++) {
        const device float *x = %%LOAD_BUFFER(concat_xs, n)%%;
        const int y_offset = y_offsets[n];
        const device int *x_shape = x_shapes + n*D;
        const device int *x_stride_in_y = x_strides_in_y + n*D;

        int x_size = 1;
        for (int d = 0; d < D; d++) {
            x_size *= x_shape[d];
        }

        while (x_index < x_size) {
            int y_index = y_offset;
            int s = x_index;
            for (int d = D-1; d >= 0; d--) {
                y_index += x_stride_in_y[d] * (s % x_shape[d]);
                s /= x_shape[d];
            }

            y[y_index] = x[x_index];

            x_index += num_threads;
        }

        x_index -= x_size;
    }
}
"""


@WebGPUDescriptorGenerator.register_handler(Concat)
def concat(op: Concat, memory_layout: MemoryLayout) -> List[Kernel]:
    xs = [op.inputs[f"x{str(i)}"] for i in range(len(op.inputs))]
    y = op.outputs["y"]
    target_axis = op.parameters["axis"]

    x_shapes = [x.shape for x in xs]

    # x_strides[i][j] is stride size of xs[i].order.axes[j] in y
    x_strides_in_y = [[] for _ in xs]
    for x, strides in zip(xs, x_strides_in_y):
        for axis in x.order.axes:
            strides.append(y.stride[y.order.axes_dict[axis]])

    # y_offsets[i] is memory offset of xs[i]'s data in y.
    y_offsets = []
    target_axis_offset = 0
    for x in xs:
        y_offsets.append(target_axis_offset * y.stride[y.order.axes_dict[target_axis]])
        target_axis_offset += x.shape_dict[target_axis]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "concat_y": memory_layout[y],
        "concat_D": len(y.shape),
        "concat_N": len(xs),
        "concat_xs": [memory_layout[x] for x in xs],
        "concat_x_strides_in_y": x_strides_in_y,
        "concat_x_shapes": x_shapes,
        "concat_y_offsets": y_offsets
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
