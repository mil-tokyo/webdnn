from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.operators.space2depth import Space2Depth
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
%%UNIFORM(float, C1)%%;

void main() {
    vec2 p_y = gl_FragCoord.xy - 0.5;
    vec4 p_Y = mod(floor((dot(p_y, s_y) + 0.5) / s_Y) + 0.5, d_Y) - 0.5;
    
    float n = p_Y.x;
    float h2 = p_Y.y;
    float w2 = p_Y.z;
    float c2 = p_Y.w;
    
    float c1 = mod(c2, C1); 
    float h1 = h2 * r + floor(floor(c2 / C1) / r); 
    float w1 = w2 * r + mod(floor(c2 / C1), r); 

    vec4 p_X = vec4(n, h1, w1, c1);
    vec2 p_x = mod(floor((dot(p_X, s_X) + 0.5) / s_x) + 0.5, d_x) - 0.5;

    float v = texture2D(X, (p_x + 0.5) / d_x).r;

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


@WebGLDescriptorGenerator.register_handler(Space2Depth)
def elementwise_add(op: Space2Depth, _: MemoryLayout) -> List[Kernel]:
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
        "C1": x.shape_dict[Axis.C],
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
