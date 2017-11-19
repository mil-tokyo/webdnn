from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import texel_fetch, get_output_position, change_order
from webdnn.graph.axis import Axis
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.order import OrderNHWC


@WebGLDescriptorGenerator.register_handler(Col2Im)
def col2im(op: Col2Im) -> List[Kernel]:
    col = op.inputs["col"]
    im = op.outputs["im"]

    assert col.order.check_same_axes(OrderNHWC)
    assert im.order.check_same_axes(OrderNHWC)
    assert ChannelMode.get(col) == ChannelModeEnum.R
    assert ChannelMode.get(im) == ChannelModeEnum.R

    code = KernelCode(["""
void main() {
    ivec4 variable_position_im = """, change_order(get_output_position(im), im.order, OrderNHWC), f""";

    int n = variable_position_im.x;
    int h1 = variable_position_im.y;
    int w1 = variable_position_im.z; 
    int c1 = variable_position_im.w;

    float sum = 0.0;

    for (int kh = 0; kh < {op.KH}; kh++) {{
        int h2 = (h1 + {op.PH} - kh) / {op.SH};
        if (mod(h1 + {op.PH} - kh, {op.SH}) != 0 || h2 < 0 || h2 >= {col.shape_dict[Axis.H]}) continue;

        for (int kw = 0; kw < {op.KW}; kw++) {{
            int w2 = (w1 + {op.PW} - kw) / {op.SW};
            if (mod(w1 + {op.PW} - kw, {op.SW}) != 0 || w2 < 0 || w2 >= {col.shape_dict[Axis.W]}) continue;

            int khkwc1 = (kh * {op.KW} + kw) * {im.shape_dict[Axis.C]} + c1;

            sum += """, texel_fetch(col, change_order("vec4(n, h2, w2, khkwc1)", OrderNHWC, col.order)), """.r;
        }
    }

    gl_FragColor.r = sum;
}
"""])
    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        im
    )]
