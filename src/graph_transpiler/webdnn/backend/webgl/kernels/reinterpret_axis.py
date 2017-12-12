from typing import List

from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import texel_fetch, change_order, get_output_position
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.order import Order


@WebGLDescriptorGenerator.register_handler(ReinterpretAxis)
def reinterpret_axis(op: ReinterpretAxis) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    y_axes_order_in_x_order = Order([op.out_order.axes[op.in_order.axes_dict[a]] for a in x.order.axes])

    # FIXME: optimize
    code = KernelCode([f"""
void main() {{
    gl_FragColor.r = """, texel_fetch(x, change_order(get_output_position(y), y.order, y_axes_order_in_x_order)), f""".r;
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
