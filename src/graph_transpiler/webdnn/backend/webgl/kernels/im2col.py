from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.operators.im2col import Im2Col
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC, OrderCNHW

header = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, im)%%;

%%UNIFORM(vec2, s_col)%%;
%%UNIFORM(vec4, d_Col)%%;
%%UNIFORM(vec4, s_Col)%%;

%%UNIFORM(vec2, d_im)%%;
%%UNIFORM(vec2, s_im)%%;
%%UNIFORM(vec4, d_Im)%%;
%%UNIFORM(vec4, s_Im)%%;

%%UNIFORM(float, C1)%%;
%%UNIFORM(float, H1)%%;
%%UNIFORM(float, W1)%%;
%%UNIFORM(float, KH)%%;
%%UNIFORM(float, KW)%%;
%%UNIFORM(float, DH)%%;
%%UNIFORM(float, DW)%%;
%%UNIFORM(float, SH)%%;
%%UNIFORM(float, SW)%%;
%%UNIFORM(float, PH)%%;
%%UNIFORM(float, PW)%%;

void main() {
    vec4 p_Col = convert_position(gl_FragCoord.xy, s_col, s_Col, d_Col) - 0.5;
"""

footer = """
    float h1 = h2 * SH - PH + kh * DH;
    float w1 = w2 * SW - PW + kw * DW;

    float v;
    if (h1 < 0.0 || h1  >= H1 || w1  < 0.0 || w1  >= W1) {
        v = 0.0;
    } else {
        vec4 p_Im = vec4(n, h1, w1, c1) + 0.5;
        vec2 p_im = convert_position(p_Im, s_Im, s_im, d_im);

        v = texture2D(im, p_im / d_im).r;
    }
    
    gl_FragColor = vec4(v, 0, 0, 0);
}"""

template_NHWC = header + """
    float n  = p_Col.x;
    float h2 = p_Col.y;
    float w2 = p_Col.z;
    float kh = mod(floor(floor(p_Col.w/ C1)/ KW) + 0.5, KH) - 0.5;
    float kw = mod(floor(p_Col.w/ C1) + 0.5, KW) - 0.5;
    float c1 = mod(p_Col.w + 0.5, C1) - 0.5;
""" + footer

template_CNHW = header + """
    float kh = mod(floor(floor(p_Col.x/ C1)/ KW) + 0.5, KH) - 0.5;
    float kw = mod(floor(p_Col.x/ C1) + 0.5, KW) - 0.5;
    float c1 = mod(p_Col.x + 0.5, C1) - 0.5;
    float n  = p_Col.y;
    float h2 = p_Col.z;
    float w2 = p_Col.w; 
""" + footer


@WebGLDescriptorGenerator.register_handler(Im2Col)
def elementwise_add(op: Im2Col, _: MemoryLayout) -> List[Kernel]:
    im = op.inputs["im"]
    col = op.outputs["col"]

    assert im.order == OrderNHWC
    assert col.order == OrderNHWC or col.order == OrderCNHW

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "im": im,

        "s_col": texture_stride(col),
        "d_Col": col.shape,
        "s_Col": col.stride,

        "d_im": texture_shape(im),
        "s_im": texture_stride(im),
        "d_Im": im.shape,
        "s_Im": im.stride,

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

    source = template_CNHW if col.order == OrderCNHW else template_NHWC
    source = name_injector.inject(source)
    source = uniform_injector.inject(source)

    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        col
    )

    return [kernel]
