from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable

template = """
precision highp float;

%%UNIFORM(sampler2D, X)%%;

%%UNIFORM(vec2, s_y)%%;
%%UNIFORM(vec4, d_Y)%%;
%%UNIFORM(vec4, s_Y)%%;

%%UNIFORM(vec2, d_x)%%;
%%UNIFORM(vec2, s_x)%%;
%%UNIFORM(vec4, d_X)%%;
%%UNIFORM(vec4, s_X)%%;

%%UNIFORM(float, r)%%;
%%UNIFORM(float, C2)%%;

void main() {
    vec4 p_Col = mod(floor(dot(gl_FragCoord.xy-0.5, s_y) / s_Y), d_Y);
    
    float n = p_Col.x;
    float h2 = p_Col.y;
    float w2 = p_Col.z;
    float c2 = p_Col.w;
    
    float c1 = c2 + mod(w2, r) * C2 + mod(h2, r) * C2 * r;
    float h1 = floor(h2 / r);
    float w1 = floor(w2 / r);

    vec4 p_X = vec4(n, h1, w1, c1);
    vec2 p_x = mod(floor(dot(mod(p_X, d_X), s_X) / s_x), d_x) + 0.5;

    float v = texture2D(X, p_x / d_x).r;

    gl_FragColor = vec4(v, 0, 0, 0);
}
"""


def texture_shape(v: Variable):
    # texture_length = (v.size + 4 - 1) // 4
    texture_length = v.size
    return [
        texture_length if texture_length < 2048 else 2048,
        (texture_length + 2048 - 1) // 2048
    ]


def texture_stride(v: Variable):
    result = []
    s = 1
    for d in texture_shape(v):
        result.append(s)
        s *= d
    return result


@WebGLDescriptorGenerator.register_handler(Depth2Space)
def elementwise_add(op: Depth2Space, _: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]
    r = op.parameters['r']

    assert x.order == OrderNHWC
    assert y.order == OrderNHWC

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X": x,

        "s_y": texture_stride(y),
        "d_Y": y.shape,
        "s_Y": y.stride,

        "d_x": texture_shape(x),
        "s_x": texture_stride(x),
        "d_X": x.shape,
        "s_X": x.stride,

        "r": r,
        "C2": y.shape_dict[Axis.C],
    })

    source = template
    source = name_injector.inject(source)
    source = uniform_injector.inject(source)

    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        y
    )

    return [kernel]
