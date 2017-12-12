from typing import List

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, Type
from webdnn.backend.webgl.kernels.util import texture_shape, change_order, convert_position, texture_stride, convert_coord, simplify_orders
from webdnn.graph.operators.concat import Concat
from webdnn.util.misc import mul


@WebGLDescriptorGenerator.register_handler(Concat)
def concat(op: Concat) -> List[Kernel]:
    xs = [op.inputs[f"x{i}"] for i in range(len(op.inputs) - 1)]
    workspace = op.inputs["workspace"]
    y = op.outputs["y"]
    axis = op.axis

    kernels = []

    # noinspection PyUnresolvedReferences
    inv_texture_shape_y = [float(np.double(1.0) / np.double(v)) for v in texture_shape(y)[:2][::-1]]

    # noinspection PyUnresolvedReferences
    inv_texture_shape_workspace = [float(np.double(1.0) / np.double(v)) for v in texture_shape(workspace)[:2][::-1]]

    sections = [0]
    for x in xs:
        sections.append(sections[-1] + x.shape_dict[axis])

    for i, x in enumerate(xs):
        assert x.order.check_same_axes(y.order)
        assert ChannelMode.get(x) == ChannelMode.get(y)

        if x.ndim > 4:
            # simplify orders
            orders, shape_dicts = simplify_orders([x, y], keep_axes=[axis])
            shapes = {v: [shape_dicts[v][a] for a in order.axes] for v, order in orders.items()}
            strides = {v: [mul(shapes[v][i + 1:]) for i in range(order.ndim)] for v, order in orders.items()}
        else:
            orders = {y: y.order, x: x.order}
            shape_dicts = {y: y.shape_dict, x: x.shape_dict}
            shapes = {y: y.shape, x: x.shape}
            strides = {y: y.stride, x: x.stride}

        # copy xs[i] or workspace's value into y
        code1 = KernelCode([f"""
void main() {{
    """, Type.Ivec.get_name(shapes[x]), f""" variable_position_x = """, change_order(
            convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], shapes[y], strides[y]),
            orders[y], orders[x]
        ), f""";
    variable_position_x[{orders[x].axes_dict[axis]}] -= {sections[i]};

    gl_FragColor.r = (
            variable_position_x[{orders[x].axes_dict[axis]}] < 0 || variable_position_x[{orders[x].axes_dict[axis]}] >= {shape_dicts[x][axis]}
        )
        ? texture2D(""", workspace, """, gl_FragCoord.xy * """, inv_texture_shape_workspace, """).r
        : texture2D(""", x, ",", convert_coord("variable_position_x", shapes[x], strides[x], texture_shape(x)[:2][::-1],
                                               texture_stride(x)[:2][::-1]), f""").r;
}}
"""], name="Concat_copy_to_y")

        # copy y's value into workspace
        code2 = KernelCode(["""
void main() { gl_FragColor = texture2D(""", y, """, gl_FragCoord.xy * """, inv_texture_shape_y, """); }
"""], name="Concat_escape_to_ws")

        source1 = code1.generate()
        source2 = code2.generate()
        kernels += [
            Kernel(
                source1,
                code1.name,
                code1.samplers,
                code1.uniforms,
                y
            ),
            Kernel(
                source2,
                code2.name,
                code2.samplers,
                code2.uniforms,
                workspace
            )
        ]

    return kernels
