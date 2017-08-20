from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.variable import Variable

template = """
precision highp float;

%%UNIFORM(sampler2D, X0)%%;
%%UNIFORM(vec2, texture_shape)%%;

void main() {
    gl_FragColor = texture2D(X0, gl_FragCoord.xy / texture_shape);
}
"""


def texture_shape(v: Variable):
    # texture_length = (v.size + 4 - 1) // 4
    texture_length = v.size
    return [
        texture_length if texture_length < 2048 else 2048,
        (texture_length + 2048 - 1) // 2048
    ]


@WebGLDescriptorGenerator.register_handler(Reshape)
def elementwise_add(op: Reshape, _: MemoryLayout) -> List[Kernel]:
    x0 = op.inputs["x0"]
    y = op.outputs["y"]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X0": x0,
        "texture_shape": texture_shape(y),
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
