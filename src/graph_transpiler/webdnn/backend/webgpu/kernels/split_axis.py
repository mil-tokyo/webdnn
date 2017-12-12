from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.split_axis import SplitAxis

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *x = %%LOAD_BUFFER(split_axis_x)%%;
    const char N = %%LOAD_BUFFER(split_axis_N)%%;
    const char D = %%LOAD_BUFFER(split_axis_D)%%;
    const device int *x_offsets = %%LOAD_BUFFER(split_axis_x_offsets)%%;
    const device int *y_shapes = %%LOAD_BUFFER(split_axis_y_shapes)%%;
    const device int *y_strides_in_x = %%LOAD_BUFFER(split_axis_y_strides_in_x)%%;

    int y_index = index;

    for (int n = 0; n < N; n++) {
        device float *y = %%LOAD_BUFFER(split_axis_ys, n)%%;
        const int x_offset = x_offsets[n];
        const device int *y_shape = y_shapes + n*D;
        const device int *y_stride_in_x = y_strides_in_x + n*D;

        int y_size = 1;
        for (int d = 0; d < D; d++) {
            y_size *= y_shape[d];
        }

        while (y_index < y_size) {
            int x_index = x_offset;
            int s = y_index;
            for (int d = D-1; d >= 0; d--) {
                x_index += y_stride_in_x[d] * (s % y_shape[d]);
                s /= y_shape[d];
            }

            y[y_index] = x[x_index];

            y_index += num_threads;
        }

        y_index -= y_size;
    }
}
"""


@WebGPUDescriptorGenerator.register_handler(SplitAxis)
def split_axis(op: SplitAxis, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    ys = [op.outputs[f"y{str(i)}"] for i in range(len(op.outputs))]
    target_axis = op.parameters["axis"]

    y_shapes = [y.shape for y in ys]

    # y_strides[i][j] is stride size of ys[i].order.axes[j] in x
    y_strides_in_x = [[x.stride_dict[axis] for axis in y.order.axes] for y in ys]

    # x_offsets[i] is memory offset of ys[i]'s data in x.
    x_offsets = []
    target_axis_offset = 0
    for y in ys:
        x_offsets.append(target_axis_offset * x.stride[x.order.axes_dict[target_axis]])
        target_axis_offset += y.shape_dict[target_axis]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "split_axis_x": memory_layout[x],
        "split_axis_D": len(x.shape),
        "split_axis_N": len(ys),
        "split_axis_ys": [memory_layout[y] for y in ys],
        "split_axis_y_strides_in_x": y_strides_in_x,
        "split_axis_y_shapes": y_shapes,
        "split_axis_x_offsets": x_offsets
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
