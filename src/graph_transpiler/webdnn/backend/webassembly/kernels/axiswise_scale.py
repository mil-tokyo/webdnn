from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.util.misc import mul


@WebassemblyDescriptorGenerator.register_handler(AxiswiseScale)
def axiswise_scale(op: AxiswiseScale,
                   memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    if x.variable.order == y.variable.order:
        return axiswise_scale_same_order(op, memory_layout)

    else:
        return axiswise_scale_general(op, memory_layout)


template_same_order = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(axiswise_scale_X)%%;
          float *Y = %%LOAD_BUFFER(axiswise_scale_Y)%%;
    const float *S = %%LOAD_BUFFER(axiswise_scale_S)%%;
    const int D1 = %%LOAD_BUFFER(axiswise_scale_D1)%%;
    const int D2 = %%LOAD_BUFFER(axiswise_scale_D2)%%;
    const int D3 = %%LOAD_BUFFER(axiswise_scale_D3)%%;

    for (int index = 0; index < D1 * D2 * D3; index++) {
        Y[index] = X[index] * S[index / D3 % D2];
    }
}
"""


def axiswise_scale_same_order(op: AxiswiseScale,
                              memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    s = memory_layout[op.inputs["s"]]
    y = memory_layout[op.outputs["y"]]

    target_axis_index = x.variable.order.axes_dict[op.axis]
    D1 = mul(x.variable.shape[:target_axis_index])
    D2 = x.variable.shape[target_axis_index]
    D3 = mul(x.variable.shape[target_axis_index + 1:])

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "axiswise_scale_X": x,
        "axiswise_scale_S": s,
        "axiswise_scale_Y": y,
        "axiswise_scale_D1": D1,
        "axiswise_scale_D2": D2,
        "axiswise_scale_D3": D3
    })

    name_injector = KernelNameInjector(op)

    source = template_same_order
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]


template_general = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(axiswise_scale_X)%%;
          float *Y = %%LOAD_BUFFER(axiswise_scale_Y)%%;
    const float *S = %%LOAD_BUFFER(axiswise_scale_S)%%;

    const int D1 = %%LOAD_BUFFER(axiswise_scale_D1)%%;
    const int D2 = %%LOAD_BUFFER(axiswise_scale_D2)%%;
    const int D3 = %%LOAD_BUFFER(axiswise_scale_D3)%%;
    const int D = %%LOAD_BUFFER(axiswise_scale_D)%%;
    const int d_target = %%LOAD_BUFFER(axiswise_scale_d_target)%%;
    const int *x_shape = %%LOAD_BUFFER(axiswise_scale_x_shape)%%;
    const int *x_stride_in_y = %%LOAD_BUFFER(axiswise_scale_x_stride_in_y)%%;

    for (int index = 0; index < D1 * D2 * D3; index++) {
        int y_offset = 0;
        int s = index;
        for (int d = D - 1; d >= 0; d--) {
            y_offset += x_stride_in_y[d] * (s % x_shape[d]);
            s /= x_shape[d];
        }

        Y[y_offset] = X[index] * S[index / D3 % D2];
    }
}
"""


def axiswise_scale_general(op: AxiswiseScale,
                           memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    s = memory_layout[op.inputs["s"]]
    y = memory_layout[op.outputs["y"]]

    x_shape = x.variable.shape

    target_axis_index = x.variable.order.axes_dict[op.axis]
    D1 = mul(x_shape[:target_axis_index])
    D2 = x_shape[target_axis_index]
    D3 = mul(x_shape[target_axis_index + 1:])

    y_strides = []
    stride = 1
    for sh in reversed(y.variable.shape):
        y_strides.insert(0, stride)
        stride *= sh

    x_stride_in_y = [y_strides[y.variable.order.axes_dict[axis]] for axis in x.variable.order.axes]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "axiswise_scale_X": x,
        "axiswise_scale_S": s,
        "axiswise_scale_Y": y,
        "axiswise_scale_D1": D1,
        "axiswise_scale_D2": D2,
        "axiswise_scale_D3": D3,
        "axiswise_scale_D": x.variable.ndim,
        "axiswise_scale_d_target": x.variable.order.axes_dict[op.axis],
        "axiswise_scale_x_shape": x_shape,
        "axiswise_scale_x_stride_in_y": x_stride_in_y,
    })

    name_injector = KernelNameInjector(op)

    source = template_general
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
