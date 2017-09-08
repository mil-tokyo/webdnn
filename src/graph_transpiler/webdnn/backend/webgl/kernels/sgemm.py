from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.operators.sgemm import Sgemm
from webdnn.backend.webgl.uniform_injector import UniformInjector

header = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, A)%%;
%%UNIFORM(sampler2D, B)%%;

%%UNIFORM(vec2, s_c)%%;
%%UNIFORM(vec2, d_C)%%;
%%UNIFORM(vec2, s_C)%%;

%%UNIFORM(vec2, d_a)%%;
%%UNIFORM(vec2, d_b)%%;

void main() {
    vec2 p_C = convert_position(gl_FragCoord.xy, s_c, s_C, d_C) - 0.5;
    
    float m = p_C.x;
    float n = p_C.y;

    float v = 0.0;
"""

footer = """
    gl_FragColor = vec4(v, 0, 0, 0);
}
"""

template_R = header + """
    for (float k = %%LOOP_SIZE%% - 1.0; k >= 0.0; k -= 1.0) {
        float v_a = texture2D(A, fract((vec2(%%INDICES_A%%) + 0.5) / d_a)).r;
        float v_b = texture2D(B, fract((vec2(%%INDICES_B%%) + 0.5) / d_b)).r;

        v += v_a * v_b;
    }
""" + footer

template_RGBA = header + """
    for (float k = 0.0; k < %%LOOP_SIZE%%; k += 4.0) {
        vec4 v_a = texture2D(A, fract((vec2(%%INDICES_A%%) + 0.5) / d_a));
        vec4 v_b = texture2D(B, fract((vec2(%%INDICES_B%%) + 0.5) / d_b));

        v += dot(v_a, v_b);
    }
""" + footer


def generate_template(mode: ChannelModeEnum, transpose_A: bool, transpose_B: bool, K: int):
    if mode == ChannelModeEnum.R:
        template = template_R

    elif mode == ChannelModeEnum.RGBA:
        template = template_RGBA

    else:
        raise NotImplementedError

    return template \
        .replace("%%LOOP_SIZE%%", f"{K:.1f}") \
        .replace("%%INDICES_A%%", "k, m" if transpose_A else "m, k") \
        .replace("%%INDICES_B%%", "n, k" if transpose_B else "k, n")


@WebGLDescriptorGenerator.register_handler(Sgemm)
def elementwise_add(op: Sgemm) -> List[Kernel]:
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]

    assert ChannelMode.get(A) == ChannelMode.get(B)

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()
    uniform_injector.register({
        "A": A,
        "B": B,

        "s_c": texture_stride(C),
        "d_C": [op.M, op.N],
        "s_C": [op.N, 1],

        "d_a": texture_shape(A),
        "d_b": texture_shape(B),

        "K": op.K
    })

    source = generate_template(mode=ChannelMode.get(A), transpose_A=op.transpose_A, transpose_B=op.transpose_B, K=op.K)
    source = uniform_injector.inject(source)
    source = name_injector.inject(source)
    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        C
    )

    return [kernel]
