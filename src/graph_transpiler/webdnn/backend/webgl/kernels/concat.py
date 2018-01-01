from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, Type
from webdnn.backend.webgl.kernels.util import texture_shape, change_order, convert_position, texture_stride, convert_coord, simplify_orders
from webdnn.graph.operators.concat import Concat
from webdnn.util.misc import mul


@WebGLDescriptorGenerator.register_handler(Concat)
def concat(op: Concat) -> List[Kernel]:
    assert len(op.inputs) == 2
    x0 = op.inputs["x0"]
    x1 = op.inputs["x1"]
    y = op.outputs["y"]
    axis = op.axis

    assert x0.order.check_same_axes(y.order)
    assert x1.order.check_same_axes(y.order)
    assert ChannelMode.get(x0) == ChannelMode.get(x1) == ChannelMode.get(y)

    if x0.ndim > 4 or x1.ndim > 4:
        # simplify orders
        orders, shape_dicts = simplify_orders([x0, x1, y], keep_axes=[axis])
        shapes = {v: [shape_dicts[v][a] for a in order.axes] for v, order in orders.items()}
        strides = {v: [mul(shapes[v][i + 1:]) for i in range(order.ndim)] for v, order in orders.items()}

    else:
        orders = {y: y.order, x0: x0.order, x1: x1.order}
        shape_dicts = {y: y.shape_dict, x0: x0.shape_dict, x1: x1.shape_dict}
        shapes = {y: y.shape, x0: x0.shape, x1: x1.shape}
        strides = {y: y.stride, x0: x0.stride, x1: x1.stride}

    code = KernelCode([f"""
void main() {{
""", Type.Ivec.get_name(shapes[x0]), f""" variable_position_x0 = """, change_order(
        convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], shapes[y], strides[y]),
        orders[y], orders[x0]
    ), f""";
""", Type.Ivec.get_name(shapes[x1]), f""" variable_position_x1 = """, change_order(
        convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], shapes[y], strides[y]),
        orders[y], orders[x1]
    ), f""";
    variable_position_x1[{orders[x1].axes_dict[axis]}] -= {x0.shape_dict[axis]};

    gl_FragColor.r = (
        (variable_position_x0[{orders[x0].axes_dict[axis]}] >= {shape_dicts[x0][axis]})
        ? texture2D(""", x1, ",", convert_coord("variable_position_x1", shapes[x1], strides[x1], texture_shape(x1)[:2][::-1],
                                                texture_stride(x1)[:2][::-1]), f""")
        : texture2D(""", x0, ",", convert_coord("variable_position_x0", shapes[x0], strides[x0], texture_shape(x0)[:2][::-1],
                                                texture_stride(x0)[:2][::-1]), f""")
    ).r;
}}
"""], name=op.__class__.__name__)
    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )]
