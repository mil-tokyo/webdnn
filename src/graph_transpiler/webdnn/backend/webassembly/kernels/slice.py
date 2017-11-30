from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.slice import Slice, normalize_slice

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const char ndim = %%LOAD_BUFFER(slice_ndim)%%;

    const float *x = %%LOAD_BUFFER(slice_X)%%;
    const int *x_stride_in_y_order = %%LOAD_BUFFER(slice_x_stride_in_y_order)%%;
    const int x_index_offset = %%LOAD_BUFFER(slice_x_index_offset)%%;

    float *y = %%LOAD_BUFFER(slice_Y)%%;
    const int y_size = %%LOAD_BUFFER(slice_y_size)%%;
    const int *y_shape = %%LOAD_BUFFER(slice_y_shape)%%;
    const int *y_stride = %%LOAD_BUFFER(slice_y_stride)%%;

    for (int y_index = 0; y_index < y_size; y_index++) {
        int x_index = x_index_offset;

        for (int d = 0; d < ndim; d++) {
            x_index += ((y_index / y_stride[d]) % y_shape[d]) * x_stride_in_y_order[d];
        }

        y[y_index] = x[x_index];
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Slice)
def slice_handler(op: Slice, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    remained_axes_in_y_order = [a for a in y.order.axes if a in x.order.axes]
    removed_axes = [a for a in x.order.axes if a not in y.order.axes]

    x_index_offset = 0
    x_strides = []

    for axis in remained_axes_in_y_order:
        assert isinstance(op.indices[axis], slice)
        index = normalize_slice(op.indices[axis], x.shape_dict[axis])
        x_index_offset += x.stride_dict[axis] * index.start
        x_strides.append(x.stride_dict[axis] * index.step)

    for axis in removed_axes:
        assert isinstance(op.indices[axis], int)
        x_index_offset += x.stride_dict[axis] * op.indices[axis]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "slice_ndim": len(remained_axes_in_y_order),

        "slice_X": memory_layout[x],
        "slice_x_stride_in_y_order": x_strides,
        "slice_x_index_offset": x_index_offset,

        "slice_Y": memory_layout[y],
        "slice_y_size": y.size,
        "slice_y_shape": [y.shape_dict[a] for a in remained_axes_in_y_order],
        "slice_y_stride": [y.stride_dict[a] for a in remained_axes_in_y_order]
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
