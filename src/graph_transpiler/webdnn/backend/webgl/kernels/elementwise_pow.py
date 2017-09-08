from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, optimize_loop_structure, texture_shape, texture_stride
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.elementwise_pow import ElementwisePow

header = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X0)%%;
%%UNIFORM(sampler2D, X1)%%;

%%UNIFORM(vec2, s_y)%%;
%%UNIFORM(vec4, d_Y)%%;
%%UNIFORM(vec4, s_Y)%%;

%%UNIFORM(vec2, d_x0)%%;
%%UNIFORM(vec2, s_x0)%%;
%%UNIFORM(vec4, d_X0)%%;
%%UNIFORM(vec4, s_X0)%%;

%%UNIFORM(vec2, d_x1)%%;
%%UNIFORM(vec2, s_x1)%%;
%%UNIFORM(vec4, d_X1)%%;
%%UNIFORM(vec4, s_X1)%%;

void main() {
    vec4 p_Y = convert_position(gl_FragCoord.xy, s_y, s_Y, d_Y);    

    vec4 p_X0 = mod(p_Y, d_X0); // for broadcasting
    vec4 p_X1 = mod(p_Y, d_X1);

    vec2 p_x0 = convert_coord(p_X0, s_X0, s_x0, d_x0);
    vec2 p_x1 = convert_coord(p_X1, s_X1, s_x1, d_x1);
"""

footer = """
}
"""

template_R = header + """
    float x0 = texture2D(X0, p_x0).r;
    float x1 = texture2D(X1, p_x1).r;
    float y;

    y = pow(x0, x1);

    gl_FragColor = vec4(y, 0, 0, 0);
""" + footer

template_RGBA = header + """
    vec4 x0 = texture2D(X0, p_x0);
    vec4 x1 = texture2D(X1, p_x1);
    vec4 y;
    
    y = pow(x0, x1);
    
    gl_FragColor = y;
""" + footer


@WebGLDescriptorGenerator.register_handler(ElementwisePow)
def elementwise_add(op: ElementwisePow) -> List[Kernel]:
    x0 = op.inputs["x0"]
    x1 = op.inputs["x1"]
    y = op.outputs["y"]

    shapes, strides = optimize_loop_structure([x0, x1, y], y)

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X0": x0,
        "X1": x1,

        "s_y": texture_stride(y),
        "d_Y": shapes[y],
        "s_Y": strides[y],

        "d_x0": texture_shape(x0),
        "s_x0": texture_stride(x0),
        "d_X0": shapes[x0],
        "s_X0": strides[x0],

        "d_x1": texture_shape(x1),
        "s_x1": texture_stride(x1),
        "d_X1": shapes[x1],
        "s_X1": strides[x1],
    })

    source = template_R if ChannelMode.get(y) == ChannelModeEnum.R else template_RGBA
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
