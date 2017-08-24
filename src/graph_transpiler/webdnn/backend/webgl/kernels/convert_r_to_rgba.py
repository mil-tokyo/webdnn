from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.uniform_injector import UniformInjector

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X0)%%;

%%UNIFORM(vec2, d_y)%%;
%%UNIFORM(vec2, s_y)%%;

%%UNIFORM(vec2, d_x0)%%;
%%UNIFORM(vec2, s_x0)%%;

void main() {
    float r = texture2D(X0, mod(floor((dot(gl_FragCoord.xy - 0.5, s_y) + 0.5) / s_x0) + 0.5, d_x0) / d_x0).r;
    float g = texture2D(X0, mod(floor((dot(gl_FragCoord.xy - 0.5, s_y) + 1.5) / s_x0) + 0.5, d_x0) / d_x0).r;
    float b = texture2D(X0, mod(floor((dot(gl_FragCoord.xy - 0.5, s_y) + 2.5) / s_x0) + 0.5, d_x0) / d_x0).r;
    float a = texture2D(X0, mod(floor((dot(gl_FragCoord.xy - 0.5, s_y) + 3.5) / s_x0) + 0.5, d_x0) / d_x0).r;
 
    gl_FragColor = vec4(r, g, b, a);
}
"""


@WebGLDescriptorGenerator.register_handler(ConvertRtoRGBA)
def convert_r_to_rgba(op: ConvertRtoRGBA) -> List[Kernel]:
    x0 = op.inputs["x0"]
    y = op.outputs["y"]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()
    uniform_injector.register({
        "X0": x0,

        "d_y": texture_shape(y),
        "s_y": texture_stride(y),

        "d_x0": texture_shape(x0),
        "s_x0": texture_stride(x0),
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
