from typing import List

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, Type
from webdnn.backend.webgl.kernels.util import texture_shape, get_output_position, texel_fetch, change_order
from webdnn.graph.operators.concat import Concat


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

        # copy xs[i] or workspace's value into y
        code1 = KernelCode([f"""
void main() {{
    """, Type.Ivec.get_name(x.shape), f""" variable_position_x = """, change_order(get_output_position(y), y.order, x.order), f""";     
    variable_position_x[{x.order.axes_dict[axis]}] -= {sections[i]};

    gl_FragColor = (
            variable_position_x[{x.order.axes_dict[axis]}] < 0 || variable_position_x[{x.order.axes_dict[axis]}] >= {x.shape_dict[axis]}
        ) 
        ? texture2D(""", workspace, """, gl_FragCoord.xy * """, inv_texture_shape_workspace, """) 
        : """, texel_fetch(x, "variable_position_x"), """;
}
"""])

        # copy y's value into workspace
        code2 = KernelCode(["""
void main() { gl_FragColor = texture2D(""", y, """, gl_FragCoord.xy * """, inv_texture_shape_y, """); }
"""])

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
