from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape, optimize_loop_structure
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.leaky_relu import LeakyRelu

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X0)%%;

%%UNIFORM(vec2, s_y)%%;
%%UNIFORM(vec4, d_Y)%%;
%%UNIFORM(vec4, s_Y)%%;

%%UNIFORM(vec2, d_x0)%%;
%%UNIFORM(vec2, s_x0)%%;
%%UNIFORM(vec4, d_X0)%%;
%%UNIFORM(vec4, s_X0)%%;

%%UNIFORM(float, slope)%%;

void main() {
    vec4 p_Y = convert_position(gl_FragCoord.xy, s_y, s_Y, d_Y);    
    vec4 p_X0 = mod(p_Y, d_X0); // for broadcasting
    vec2 p_x0 = convert_coord(p_X0, s_X0, s_x0, d_x0);

    vec4 x0 = texture2D(X0, p_x0);
    vec4 y;
    
    y = ((1.0 + slope) * x0 + (1.0 - slope) * abs(x0)) * 0.5;
    
    gl_FragColor = y;
}
"""


@WebGLDescriptorGenerator.register_handler(LeakyRelu)
def elementwise_add(op: LeakyRelu) -> List[Kernel]:
    x0 = op.inputs["x0"]
    y = op.outputs["y"]

    shapes, strides = optimize_loop_structure([x0, y], y)

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X0": x0,

        "s_y": texture_stride(y),
        "d_Y": shapes[y],
        "s_Y": strides[y],

        "d_x0": texture_shape(x0),
        "s_x0": texture_stride(x0),
        "d_X0": shapes[x0],
        "s_X0": strides[x0],

        "slope": op.parameters["slope"]
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
