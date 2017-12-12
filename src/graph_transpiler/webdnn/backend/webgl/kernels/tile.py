from typing import List

from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, ExpressionNode
from webdnn.backend.webgl.kernels.util import change_order, get_output_position, ivec, texel_fetch
from webdnn.graph.operators.tile import Tile


@WebGLDescriptorGenerator.register_handler(Tile)
def reshape(op: Tile) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    # y -{broadcast}-> x_position_in_y_order -{change_order}-> x
    code = KernelCode([f"""
void main() {{
    gl_FragColor.r = """, texel_fetch(x, change_order(
        ExpressionNode(["mod(", get_output_position(y), ", ", ivec([x.shape_dict[a] for a in y.order.axes]), ")"]),
        y.order, x.order
    )), f""".r;
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
