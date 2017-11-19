from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, Type
from webdnn.backend.webgl.kernels.util import get_output_position, texel_fetch, change_order
from webdnn.graph.operators.split_axis import SplitAxis


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

        code = KernelCode([f"""
void main() {{
    """, Type.Ivec.get_name(x.shape), f""" variable_position_x = """, change_order(get_output_position(y), y.order, x.order), f""";     
    variable_position_x[{x.order.axes_dict[axis]}] += {sections[i]};
    
    gl_FragColor.r = """, texel_fetch(x, "variable_position_x"), f""".r;
}}
"""])
        source = code.generate()
        kernels.append(Kernel(
            source,
            code.name,
            code.samplers,
            code.uniforms,
            y
        ))

    return kernels
