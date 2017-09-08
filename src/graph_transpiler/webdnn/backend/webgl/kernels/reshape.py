from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_shape, texture_stride
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.reshape import Reshape

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X)%%;

%%UNIFORM(vec2, s_y)%%;

%%UNIFORM(vec2, d_x)%%;
%%UNIFORM(vec2, s_x)%%;

void main() {
    float x = texture2D(X, fract((floor((dot(gl_FragCoord.xy - 0.5, s_y) + 0.5) / s_x) + 0.5) / d_x)).r;
    gl_FragColor = vec4(x, 0, 0, 0);
}
"""


@WebGLDescriptorGenerator.register_handler(Reshape)
def elementwise_add(op: Reshape) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X": x,

        "s_y": texture_stride(y),

        "d_x": texture_shape(x),
        "s_x": texture_stride(x),
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
