from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X)%%;
%%UNIFORM(vec2, texture_shape)%%;

void main() {
    gl_FragColor = texture2D(X, gl_FragCoord.xy / texture_shape); 
}
"""


@WebGLDescriptorGenerator.register_handler(ReinterpretAxis)
def elementwise_add(op: ReinterpretAxis) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X": x,
        "texture_shape": texture_shape(y),
    })

    source = template
    source = uniform_injector.inject(source)
    source = name_injector.inject(source)
    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        y
    )

    return [kernel]
