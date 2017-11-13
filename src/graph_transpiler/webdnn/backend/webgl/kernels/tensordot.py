from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.util.misc import mul

header = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, A)%%;
%%UNIFORM(sampler2D, B)%%;

%%UNIFORM(vec2, s_c)%%;
%%UNIFORM(vec2, d_C)%%;
%%UNIFORM(vec2, s_C)%%;

%%UNIFORM(vec2, d_a)%%;
%%UNIFORM(vec2, d_b)%%;

void main() {
    ivec2 p_C = convert_position_i(gl_FragCoord.xy, s_c, s_C, d_C);
    
    int m = p_C.x;
    int n = p_C.y;

    float v = 0.0;
"""

footer = """
    gl_FragColor = vec4(v, 0, 0, 0);
}
"""

template_R = header + """
    for (int k = 0; k < %%LOOP_SIZE%%; k++) {
        float v_a = texture2D(A, fract((vec2(k, m) + 0.5) / d_a)).r;
        float v_b = texture2D(B, fract((vec2(k, n) + 0.5) / d_b)).r;

        v += v_a * v_b;
    }
""" + footer

template_RGBA = header + """
    for (int k = 0; k < %%LOOP_SIZE%%; k++) {
        vec4 v_a = texture2D(A, fract((vec2(k, m) + 0.5) / d_a));
        vec4 v_b = texture2D(B, fract((vec2(k, n) + 0.5) / d_b));

        v += dot(v_a, v_b);
    }
""" + footer


def generate_template(mode: ChannelModeEnum, reduction_size: int):
    if mode == ChannelModeEnum.R:
        template = template_R

    elif mode == ChannelModeEnum.RGBA:
        template = template_RGBA

    else:
        raise NotImplementedError

    return template.replace("%%LOOP_SIZE%%", f"{reduction_size // ChannelMode.elements_per_pixel(mode)}")


@WebGLDescriptorGenerator.register_handler(Tensordot)
def tensordot(op: Tensordot) -> List[Kernel]:
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]
    axes = op.axes

    assert ChannelMode.get(A) == ChannelMode.get(B)
    assert ChannelMode.get(C) == ChannelModeEnum.R

    # Reduced axes must be located on inside of input variables.
    assert A.order.axes[-len(axes[0]):] == axes[0]
    assert B.order.axes[-len(axes[1]):] == axes[1]

    # output variable's axes order must be as [*a_remained_axes, *b_remained_axes]
    assert C.order.axes[:A.ndim - len(axes[0])] == A.order.axes[:-len(axes[0])]
    assert C.order.axes[-(B.ndim - len(axes[1])):] == B.order.axes[:-len(axes[1])]
    assert C.ndim == A.ndim - len(axes[0]) + B.ndim - len(axes[1])

    K = mul(A.shape[-len(axes[0]):])
    M = A.size // K
    N = B.size // K

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()
    uniform_injector.register({
        "A": A,
        "B": B,

        "s_c": texture_stride(C),
        "d_C": [M, N],
        "s_C": [N, 1],

        "d_a": texture_shape(A),
        "d_b": texture_shape(B),

        "K": K
    })

    source = generate_template(mode=ChannelMode.get(A), reduction_size=K)
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
