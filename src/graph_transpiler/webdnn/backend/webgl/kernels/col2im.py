from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import get_output_position, change_order, convert_coord, texture_shape, texture_stride
from webdnn.graph.axis import Axis
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.order import OrderNHWC, Order
from webdnn.util.misc import mul


@WebGLDescriptorGenerator.register_handler(Col2Im)
def col2im(op: Col2Im) -> List[Kernel]:
    col = op.inputs["col"]
    im = op.outputs["im"]

    assert col.order.check_same_axes(Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C]))
    assert col.order.axes_dict[Axis.KH] + 2 == col.order.axes_dict[Axis.KW] + 1 == col.order.axes_dict[Axis.C] == 5
    assert im.order.check_same_axes(OrderNHWC)
    assert ChannelMode.get(col) == ChannelModeEnum.R
    assert ChannelMode.get(im) == ChannelModeEnum.R

    col_shape = col.shape[0:3] + (mul(col.shape[3:6]),)
    col_stride = [mul(col_shape[i + 1:]) for i in range(len(col_shape))]
    col_order = Order(col.order.axes[0:3] + (Axis.C,))

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

            sum += texture2D(""", col, ",", convert_coord(change_order("vec4(n, h2, w2, khkwc1)", OrderNHWC, col_order),
                                                          col_shape, col_stride,
                                                          texture_shape(col)[:2][::-1], texture_stride(col)[:2][::-1]), """).r;
        }
    }

    gl_FragColor.r = sum;
}
"""], name=op.__class__.__name__)
    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        im
    )]
