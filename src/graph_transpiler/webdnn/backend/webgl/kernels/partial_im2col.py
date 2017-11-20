from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import texel_fetch, change_order, vec, convert_position, texture_shape, \
    texture_stride
from webdnn.backend.webgl.operators.partial_im2col import PartialIm2Col
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC, Order
from webdnn.util.misc import mul


@WebGLDescriptorGenerator.register_handler(PartialIm2Col)
def partial_im2col(op: PartialIm2Col) -> List[Kernel]:
    im = op.inputs["im"]
    cols = [op.outputs[f"col{i}"] for i in range(len(op.outputs))]
    sections = [0] + op.sections
    axis = op.axis
    H1 = im.shape_dict[Axis.H]
    W1 = im.shape_dict[Axis.W]
    C1 = im.shape_dict[Axis.C]
    kernels = []

    for i, col in enumerate(cols):
        assert col.order.check_same_axes(Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C]))
        assert col.order.axes_dict[Axis.KH] + 2 == col.order.axes_dict[Axis.KW] + 1 == col.order.axes_dict[Axis.C] == 5
        assert im.order.check_same_axes(OrderNHWC)
        assert ChannelMode.get(im) == ChannelModeEnum.R

        col_shape = col.shape[0:3] + (mul(col.shape[3:6]),)
        col_stride = [mul(col_shape[i + 1:]) for i in range(len(col_shape))]
        col_order = Order(col.order.axes[0:3] + (Axis.C,))

        if ChannelMode.get(col) == ChannelModeEnum.R:
            code = KernelCode(["""
void main() {
    ivec4 variable_position_col = """, change_order(
                convert_position("gl_FragCoord.yx", texture_shape(col)[:2], texture_stride(col)[:2], col_shape, col_stride),
                col_order, OrderNHWC), f""";

    variable_position_col[{OrderNHWC.axes_dict[axis]}] += {sections[i]};

    int n  = variable_position_col.x;
    int h2 = variable_position_col.y;
    int w2 = variable_position_col.z;
    int khkwc1 = variable_position_col.w;

    int kh = khkwc1 / {C1} / {op.KW};
    int kw = khkwc1 / {C1} - kh * {op.KW};
    int c1 = khkwc1 - (kh * {op.KW} + kw) * {C1};

    int h1 = h2 * {op.SH} - {op.PH} + kh * {op.DH};
    int w1 = w2 * {op.SW} - {op.PW} + kw * {op.DW};

    if (h1 < 0 || h1 >= {H1} || w1 < 0 || w1 >= {W1}) {{
        gl_FragColor.r = 0.0;
    }} else {{
        gl_FragColor.r = """, texel_fetch(im, change_order("vec4(n, h1, w1, c1)", OrderNHWC, im.order)), f""".r;
    }}
}}
"""], name="PartialIm2Col_R")

        elif ChannelMode.get(col) == ChannelModeEnum.RGBA:
            code = KernelCode(["""
void main() {
    ivec4 variable_position_col = """, change_order(
                convert_position("gl_FragCoord.yx", texture_shape(col)[:2], texture_stride(col)[:2], col_shape, col_stride),
                col_order, OrderNHWC), f""";

    variable_position_col[{OrderNHWC.axes_dict[axis]}] += {sections[i]};

    int n  = variable_position_col.x;
    int h2 = variable_position_col.y;
    int w2 = variable_position_col.z;
    int khkwc1 = variable_position_col.w;

    int kh = khkwc1 / {C1} / {op.KW};
    int kw = khkwc1 / {C1} - kh * {op.KW};
    int c1 = khkwc1 - (kh * {op.KW} + kw) * {C1};

    int h1 = h2 * {op.SH} - {op.PH} + kh * {op.DH};
    int w1 = w2 * {op.SW} - {op.PW} + kw * {op.DW};

    if (h1 < 0 || h1 >= {H1} || w1 < 0 || w1 >= {W1}) {{
        gl_FragColor = {vec([0, 0, 0, 0])};
    }} else {{
        gl_FragColor.r = """, texel_fetch(im, change_order("vec4(n, h1, w1, c1 + 0)", OrderNHWC, im.order)), f""".r;
        gl_FragColor.g = """, texel_fetch(im, change_order("vec4(n, h1, w1, c1 + 1)", OrderNHWC, im.order)), f""".r;
        gl_FragColor.b = """, texel_fetch(im, change_order("vec4(n, h1, w1, c1 + 2)", OrderNHWC, im.order)), f""".r;
        gl_FragColor.a = """, texel_fetch(im, change_order("vec4(n, h1, w1, c1 + 3)", OrderNHWC, im.order)), f""".r;
    }}
}}
"""], name="PartialIm2Col_RGBA")

        else:
            raise NotImplementedError

        source = code.generate()
        kernels.append(Kernel(
            source,
            code.name,
            code.samplers,
            code.uniforms,
            col
        ))

    return kernels
