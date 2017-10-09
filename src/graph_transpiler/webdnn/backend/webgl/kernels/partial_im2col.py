from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.operators.partial_im2col import PartialIm2Col
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC

header = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, sampler_im)%%;

%%UNIFORM(vec2, texture_stride_col)%%;
%%UNIFORM(vec4, variable_shape_col)%%;
%%UNIFORM(vec4, variable_stride_col)%%;

%%UNIFORM(vec2, texture_shape_im)%%;
%%UNIFORM(vec2, texture_stride_im)%%;
%%UNIFORM(vec4, variable_shape_im)%%;
%%UNIFORM(vec4, variable_stride_im)%%;

%%UNIFORM(vec4, offset_col)%%;

%%UNIFORM(int, C1)%%;
%%UNIFORM(int, H1)%%;
%%UNIFORM(int, W1)%%;
%%UNIFORM(int, KH)%%;
%%UNIFORM(int, KW)%%;
%%UNIFORM(int, DH)%%;
%%UNIFORM(int, DW)%%;
%%UNIFORM(int, SH)%%;
%%UNIFORM(int, SW)%%;
%%UNIFORM(int, PH)%%;
%%UNIFORM(int, PW)%%;

void main() {
    ivec4 variable_position_col = convert_position_i(gl_FragCoord.xy, texture_stride_col, variable_stride_col, variable_shape_col) + ivec4(offset_col);

    int n  = variable_position_col.x;
    int h2 = variable_position_col.y;
    int w2 = variable_position_col.z;
    int khkwc1 = variable_position_col.w;
    int kh = khkwc1 / C1 / KW;
    int kw = khkwc1 / C1 - kh * KW;
    int c1 = khkwc1 - (kh * KW + kw) * C1;

    int h1 = h2 * SH - PH + kh * DH;
    int w1 = w2 * SW - PW + kw * DW;
"""
footer = """
}
"""

template_R = header + """
    float v = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0.0 : texture2D(sampler_im, convert_coord(vec4(n, h1, w1, c1) + 0.5, variable_stride_im, texture_stride_im, texture_shape_im)).r;

    gl_FragColor = vec4(v, 0, 0, 0);
""" + footer

template_RGBA = header + """
    float v0 = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0.0 : texture2D(sampler_im, convert_coord(vec4(n, h1, w1, c1 + 0) + 0.5, variable_stride_im, texture_stride_im, texture_shape_im)).r;
    float v1 = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0.0 : texture2D(sampler_im, convert_coord(vec4(n, h1, w1, c1 + 1) + 0.5, variable_stride_im, texture_stride_im, texture_shape_im)).r;
    float v2 = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0.0 : texture2D(sampler_im, convert_coord(vec4(n, h1, w1, c1 + 2) + 0.5, variable_stride_im, texture_stride_im, texture_shape_im)).r;
    float v3 = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0.0 : texture2D(sampler_im, convert_coord(vec4(n, h1, w1, c1 + 3) + 0.5, variable_stride_im, texture_stride_im, texture_shape_im)).r;
    
    gl_FragColor = vec4(v0, v1, v2, v3);
""" + footer


@WebGLDescriptorGenerator.register_handler(PartialIm2Col)
def partial_im2col(op: PartialIm2Col) -> List[Kernel]:
    im = op.inputs["im"]
    cols = [op.outputs[f"col{i}"] for i in range(len(op.outputs))]
    sections = [0] + op.sections
    axis = op.axis

    kernels = []

    for i, col in enumerate(cols):
        assert im.order == col.order == OrderNHWC
        assert ChannelMode.get(im) == ChannelModeEnum.R

        name_injector = KernelNameInjector(op)
        uniform_injector = UniformInjector()

        offset = [sections[i] if a == axis else 0 for a in col.order.axes]
        uniform_injector.register({
            "sampler_im": im,

            "texture_stride_col": texture_stride(col),
            "variable_shape_col": col.shape,
            "variable_stride_col": col.stride,
            "offset_col": offset,

            "texture_shape_im": texture_shape(im),
            "texture_stride_im": texture_stride(im),
            "variable_shape_im": im.shape,
            "variable_stride_im": im.stride,

            "C1": im.shape_dict[Axis.C],
            "H1": im.shape_dict[Axis.H],
            "W1": im.shape_dict[Axis.W],
            "KH": op.KH,
            "KW": op.KW,
            "DH": op.DH,
            "DW": op.DW,
            "SH": op.SH,
            "SW": op.SW,
            "PH": op.PH,
            "PW": op.PW,
        })

        source = template_R if ChannelMode.get(col) == ChannelModeEnum.R else template_RGBA
        source = uniform_injector.inject(source)
        source = name_injector.inject(source)
        kernel = Kernel(
            source,
            name_injector.name,
            uniform_injector.samplers,
            uniform_injector.uniforms,
            col
        )
        kernels.append(kernel)

    return kernels
