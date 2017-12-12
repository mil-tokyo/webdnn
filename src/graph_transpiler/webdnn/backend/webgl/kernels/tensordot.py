from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelModeEnum, ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import texture_stride, texture_shape, convert_position, vec
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.util.misc import mul


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

    if ChannelMode.get(A) == ChannelModeEnum.R:
        code = KernelCode([f"""
void main() {{
    ivec2 variable_position_c = """, convert_position("gl_FragCoord.yx", texture_shape(C)[:2], texture_stride(C)[:2], [M, N], [N, 1]), f""";

    int m = variable_position_c.x;
    int n = variable_position_c.y;

    float v = 0.0;

    for (int k = 0; k < {int(K)}; k++) {{
        float v_a = texture2D(""", A, f""", (vec2(k, m) + 0.5) * """, vec([1.0 / K, 1.0 / M]), f""").r;
        float v_b = texture2D(""", B, f""", (vec2(k, n) + 0.5) * """, vec([1.0 / K, 1.0 / N]), f""").r;

        v += v_a * v_b;
    }}

    gl_FragColor.r = v;
}}
"""], name="Tensordot_R")

    elif ChannelMode.get(A) == ChannelModeEnum.RGBA:
        code = KernelCode([f"""
void main() {{
    ivec2 variable_position_c = """, convert_position("gl_FragCoord.yx", texture_shape(C)[:2], texture_stride(C)[:2], [M, N], [N, 1]), f""";

    int m = variable_position_c.x;
    int n = variable_position_c.y;

    float v = 0.0;

    for (int k = 0; k < {int(K // 4)}; k++) {{
        vec4 v_a = texture2D(""", A, f""", (vec2(k, m) + 0.5) * """, vec([1.0 / (K // 4), 1.0 / M]), f""");
        vec4 v_b = texture2D(""", B, f""", (vec2(k, n) + 0.5) * """, vec([1.0 / (K // 4), 1.0 / N]), f""");

        v += dot(v_a, v_b);
    }}

    gl_FragColor.r = v;
}}
"""], name="Tensordot_RGBA")

    else:
        raise NotImplementedError

    source = code.generate()
    kernel = Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        C
    )

    return [kernel]
