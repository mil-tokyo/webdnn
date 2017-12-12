from typing import List

from webdnn.graph.axis import Axis
from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, ExpressionNode
from webdnn.backend.webgl.kernels.util import texture_shape, texture_stride, convert_position, convert_coord
from webdnn.graph.operators.slice import Slice, normalize_slice


@WebGLDescriptorGenerator.register_handler(Slice)
def slice_handler(op: Slice) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert ChannelMode.get(x) == ChannelMode.get(y) == ChannelModeEnum.R

    x_shape = []
    x_stride = []
    x_index_offset = 0
    y_shape = []
    y_stride = []

    x_stride_dict = x.stride_dict
    y_shape_dict = y.shape_dict
    y_stride_dict = y.stride_dict
    x_axes = list(x.order.axes)

    # reduce number of axis
    flag_removed = False
    merge_target = None  # type: Axis
    for axis in reversed(x.order.axes):
        if not isinstance(op.indices[axis], slice):
            flag_removed = False
            merge_target = None
            continue

        index = normalize_slice(op.indices[axis], x.shape_dict[axis])
        if index.start != 0 or index.stop != x.shape_dict[axis] or index.step != 1:
            flag_removed = False
            merge_target = None
            continue

        # This axis is not changed, so it can be simplified
        if flag_removed:
            del x_stride_dict[axis]
            x_axes.remove(axis)
            del y_stride_dict[axis]
            y_shape_dict[merge_target] *= y_shape_dict[axis]
            del y_shape_dict[axis]

        else:
            flag_removed = True
            merge_target = axis

    for axis in x_axes:
        if isinstance(op.indices[axis], slice):
            index = normalize_slice(op.indices[axis], x.shape_dict[axis])
            x_shape.append(y_shape_dict[axis])
            x_stride.append(x_stride_dict[axis] * index.step)
            x_index_offset += x_stride_dict[axis] * index.start
            y_shape.append(y_shape_dict[axis])
            y_stride.append(y_stride_dict[axis])

        elif isinstance(op.indices[axis], int):
            x_index_offset += x_stride_dict[axis] * op.indices[axis]

    if len(y_shape) == 1:
        y_shape.append(0)
        y_stride.append(1)
        x_stride.append(0)
        x_shape.append(0)

    code = KernelCode(["""
void main() {
    gl_FragColor.r = texture2D(""", x, ", (", convert_coord(
        ExpressionNode([
            convert_position(
                "gl_FragCoord.yx",
                texture_shape(y)[:2], texture_stride(y)[:2], y_shape, y_stride
            )
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
