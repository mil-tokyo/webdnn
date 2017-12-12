from typing import List

from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import get_output_position, texel_fetch, change_order
from webdnn.graph.axis import Axis
from webdnn.graph.operators.unpooling_2d import Unpooling2D
from webdnn.graph.order import OrderNHWC


@WebGLDescriptorGenerator.register_handler(Unpooling2D)
def average_pooling_2d(op: Unpooling2D) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order.check_same_axes(OrderNHWC)
    assert y.order.check_same_axes(OrderNHWC)

    code = KernelCode([f"""
void main() {{
    ivec4 variable_position_y = """, change_order(get_output_position(y), y.order, OrderNHWC), f""";
    int n = variable_position_y.x;
    int h2 = variable_position_y.y;
    int w2 = variable_position_y.z;
    int c = variable_position_y.w;

    float sum = 0.0;

    for (int kh = 0; kh < {op.KH}; kh++) {{
        int h1 = h2 + {op.PH} - kh;
        if (h1 < 0 || h1 >= {x.shape_dict[Axis.H]} * {op.SH}) continue;
        if (mod(h1, {op.SH}) != 0) continue;
        h1 /= {op.SH};
        for (int kw = 0; kw < {op.KW}; kw++) {{
            int w1 = w2 + {op.PW} - kw;
            if (w1 < 0 || w1 >= {x.shape_dict[Axis.W]} * {op.SW}) continue;
            if (mod(w1, {op.SW}) != 0) continue;
            w1 /= {op.SW};

            sum += """, texel_fetch(x, change_order("vec4(n, h1, w1, c)", OrderNHWC, x.order)), f""".r;
        }}
    }}

    gl_FragColor.r = sum;
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
