from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.abs import Abs
from webdnn.graph.variable import Variable

template = """
precision highp float;

%%UNIFORM(sampler2D, im)%%;

%%UNIFORM(vec2, d_y)%%;
%%UNIFORM(vec2, s_y)%%;
%%UNIFORM(vec4, d_Y)%%;
%%UNIFORM(vec4, s_Y)%%;

%%UNIFORM(vec2, d_x0)%%;
%%UNIFORM(vec2, s_x0)%%;
%%UNIFORM(vec4, d_X0)%%;
%%UNIFORM(vec4, s_X0)%%;

void main() {
    vec4 p_Y = mod(floor(dot(gl_FragCoord.xy-0.5, s_y)/s_Y), d_Y);
    vec2 p_x0 = mod(floor(dot(mod(p_Y, d_X0), s_X0)/s_x0), d_x0) + 0.5;

    float x0 = texture2D(X0, p_x0 / d_x0).r;
    float y;
    
    y = abs(x0);
    
    gl_FragColor = vec4(y, 0, 0, 0);
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


@WebGLDescriptorGenerator.register_handler(Abs)
def elementwise_add(op: Abs, _: MemoryLayout) -> List[Kernel]:
    im = op.inputs["im"]
    col = op.outputs["col"]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "im": im,

        "s_y": texture_stride(y),
        "d_y": texture_shape(y),
        "d_Y": shapes[y],
        "s_Y": strides[y],

        "d_x0": texture_shape(x0),
        "s_x0": texture_stride(x0),
        "d_X0": shapes[x0],
        "s_X0": strides[x0],
    })

    source = template
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
