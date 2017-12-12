from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, Type
from webdnn.backend.webgl.kernels.util import change_order, simplify_orders, convert_position, \
    texture_shape, texture_stride, convert_coord
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.util.misc import mul


@WebGLDescriptorGenerator.register_handler(SplitAxis)
def split_axis(op: SplitAxis) -> List[Kernel]:
    x = op.inputs["x"]
    ys = [op.outputs[f"y{i}"] for i in range(len(op.outputs))]
    sections = [0] + op.sections
    axis = op.axis

    kernels = []

    for i, y in enumerate(ys):
        assert x.order.check_same_axes(y.order)
        assert ChannelMode.get(x) == ChannelMode.get(y) == ChannelModeEnum.R

        if x.ndim > 4:
            # simplify orders
            orders, shape_dicts = simplify_orders([x, y], keep_axes=[axis])
            shapes = {v: [shape_dicts[v][a] for a in order.axes] for v, order in orders.items()}
            strides = {v: [mul(shapes[v][i + 1:]) for i in range(order.ndim)] for v, order in orders.items()}
        else:
            orders = {y: y.order, x: x.order}
            shapes = {y: y.shape, x: x.shape}
            strides = {y: y.stride, x: x.stride}

        code = KernelCode([f"""
void main() {{
    """, Type.Ivec.get_name(shapes[x]), f""" variable_position_x = """, change_order(
            convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], shapes[y], strides[y]),
            orders[y], orders[x]
        ), f""";
    variable_position_x[{orders[x].axes_dict[axis]}] += {sections[i]};

    gl_FragColor.r = texture2D(""", x, ",", convert_coord("variable_position_x", shapes[x], strides[x], texture_shape(x)[:2][::-1],
                                                          texture_stride(x)[:2][::-1]), f""").r;
}}
"""], name=op.__class__.__name__)
        source = code.generate()
        kernels.append(Kernel(
            source,
            code.name,
            code.samplers,
            code.uniforms,
            y
        ))

    return kernels
