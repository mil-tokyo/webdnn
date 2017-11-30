from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, ExpressionNode
from webdnn.backend.webgl.kernels.util import texture_shape, texture_stride, change_order, convert_position, convert_coord
from webdnn.graph.operators.slice import Slice, normalize_slice


@WebGLDescriptorGenerator.register_handler(Slice)
def slice_handler(op: Slice) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert ChannelMode.get(x) == ChannelMode.get(y) == ChannelModeEnum.R

    remained_axes_in_y_order = [a for a in y.order.axes if a in x.order.axes]
    remained_axes_in_x_order = [a for a in x.order.axes if a in y.order.axes]
    removed_axes = [a for a in x.order.axes if a not in y.order.axes]

    x_shape = []
    x_stride = []
    x_index_offset = 0
    y_shape = []
    y_stride = []

    for axis in x.order.axes:
        if isinstance(op.indices[axis], slice):
            index = normalize_slice(op.indices[axis], x.shape_dict[axis])
            x_shape.append(y.shape_dict[axis])
            x_stride.append(x.stride_dict[axis] * index.step)
            x_index_offset += x.stride_dict[axis] * index.start
            y_shape.append(y.shape_dict[axis])
            y_stride.append(y.stride_dict[axis])

        elif isinstance(op.indices[axis], int):
            x_shape.append(0)
            x_stride.append(0)  # to ignore remove axes' index, set stride as 0
            x_index_offset += x.stride_dict[axis] * op.indices[axis]
            y_shape.append(0)
            y_stride.append(1)

    code = KernelCode(["""
void main() {
    gl_FragColor.r = texture2D(""", x, ", (", convert_coord(
        ExpressionNode([
            change_order(
                convert_position(
                    "gl_FragCoord.yx",
                    texture_shape(y)[:2], texture_stride(y)[:2], y_shape, y_stride
                ),
                x.order,  # Order(remained_axes_in_y_order + removed_axes),
                x.order,  # Order(remained_axes_in_x_order + removed_axes)
            ),
        ]),
        x_shape,
        x_stride,
        texture_shape(x)[:2],
        texture_stride(x)[:2],
        x_index_offset
    ), """).yx).r;
}
"""], name="Slice")

    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )]
