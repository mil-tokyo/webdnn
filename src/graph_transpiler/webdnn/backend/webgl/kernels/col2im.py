from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.operators.col2im import Col2Im
from webdnn.graph.order import OrderNHWC

template_R = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, col)%%;

%%UNIFORM(vec2, s_im)%%;
%%UNIFORM(vec4, d_Im)%%;
%%UNIFORM(vec4, s_Im)%%;

%%UNIFORM(vec2, d_col)%%;
%%UNIFORM(vec2, s_col)%%;
%%UNIFORM(vec4, d_Col)%%;
%%UNIFORM(vec4, s_Col)%%;

%%UNIFORM(int, H2)%%;
%%UNIFORM(int, W2)%%;
%%UNIFORM(int, C1)%%;
%%UNIFORM(int, SH)%%;
%%UNIFORM(int, SW)%%;
%%UNIFORM(int, PH)%%;
%%UNIFORM(int, PW)%%;

void main() {
    ivec4 p_Im = convert_position_i(gl_FragCoord.xy, s_im, s_Im, d_Im);

    int n  = p_Im.x;
    int h1 = p_Im.y;
    int w1 = p_Im.z;
    int c1 = p_Im.w;

    float sum = 0.0;
    
    for (int kh = 0; kh < %%LOOP_SIZE_KH%%; kh++) {
        int h2 = (h1 + PH - kh) / SH;
        if (mod(h1 + PH - kh, SH) != 0 || h2 < 0 || h2 >= H2) continue;

        for (int kw = 0; kw < %%LOOP_SIZE_KW%%; kw++) {
            int w2 = (w1 + PW - kw) / SW;
            if (mod(w1 + PW - kw, SW) != 0 || w2 < 0 || w2 >= W2) continue;

            int khkwc1 = (kh * %%LOOP_SIZE_KW%% + kw) * C1 + c1; 
            sum += texture2D(col, convert_coord(vec4(n, h2, w2, khkwc1) + 0.5, s_Col, s_col, d_col)).r;
        }
    }

    gl_FragColor = vec4(sum, 0, 0, 0);
}
"""


def generate_template(op: Col2Im):
    return template_R \
        .replace("%%LOOP_SIZE_KH%%", f"{op.KH}") \
        .replace("%%LOOP_SIZE_KW%%", f"{op.KW}")


@WebGLDescriptorGenerator.register_handler(Col2Im)
def col2im(op: Col2Im) -> List[Kernel]:
    col = op.inputs["col"]
    im = op.outputs["im"]

    assert col.order == OrderNHWC
    assert im.order == OrderNHWC
    assert ChannelMode.get(col) == ChannelModeEnum.R
    assert ChannelMode.get(im) == ChannelModeEnum.R

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "col": col,

        "s_im": texture_stride(im),
        "d_Im": im.shape,
        "s_Im": im.stride,

        "d_col": texture_shape(col),
        "s_col": texture_stride(col),
        "d_Col": col.shape,
        "s_Col": col.stride,

        "H2": col.shape_dict[Axis.H],
        "W2": col.shape_dict[Axis.W],
        "C1": im.shape_dict[Axis.C],
        "SH": op.SH,
        "SW": op.SW,
        "PH": op.PH,
        "PW": op.PW,
    })

    source = generate_template(op)
    source = uniform_injector.inject(source)
    source = name_injector.inject(source)
    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        im
    )

    return [kernel]
