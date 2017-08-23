from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.backend.webgl.uniform_injector import UniformInjector

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X0)%%;

%%UNIFORM(vec2, s_y)%%;

%%UNIFORM(vec2, d_x0)%%;
%%UNIFORM(vec2, s_x0)%%;

void main() {
    float index = dot(gl_FragCoord.xy - 0.5, s_y);
    float c = floor(mod(index + 0.5, 4.0));
    vec2 hw_x0 = mod(floor((index + 0.5) / s_x0) + 0.5, d_x0);

    if (c == 0.0) {
        gl_FragColor = vec4(texture2D(X0, hw_x0 / d_x0).r, 0, 0, 0);

    } else if (c == 1.0) {
        gl_FragColor = vec4(texture2D(X0, hw_x0 / d_x0).g, 0, 0, 0);

    } else if (c == 2.0) {
        gl_FragColor = vec4(texture2D(X0, hw_x0 / d_x0).b, 0, 0, 0);

    } else if (c == 3.0) {
        gl_FragColor = vec4(texture2D(X0, hw_x0 / d_x0).a, 0, 0, 0);
    }
}
"""


@WebGLDescriptorGenerator.register_handler(ConvertRGBAtoR)
def convert_rgba_to_r(op: ConvertRGBAtoR) -> List[Kernel]:
    x0 = op.inputs["x0"]
    y = op.outputs["y"]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()
    uniform_injector.register({
        "X0": x0,

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
