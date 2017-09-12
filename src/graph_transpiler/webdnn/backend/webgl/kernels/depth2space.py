from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.operators.depth2space import Depth2Space
from webdnn.graph.order import OrderNHWC

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X)%%;

%%UNIFORM(vec2, s_y)%%;
%%UNIFORM(vec4, d_Y)%%;
%%UNIFORM(vec4, s_Y)%%;

%%UNIFORM(vec2, d_x)%%;
%%UNIFORM(vec2, s_x)%%;
%%UNIFORM(vec4, d_X)%%;
%%UNIFORM(vec4, s_X)%%;

%%UNIFORM(int, r)%%;
%%UNIFORM(int, C2)%%;

void main() {
    vec4 p_Y = convert_position(gl_FragCoord.xy, s_y, s_Y, d_Y);    
    
    int n = int(p_Y.x);
    int h2 = int(p_Y.y);
    int w2 = int(p_Y.z);
    int c2 = int(p_Y.w);
    int h1 = h2 / r;
    int w1 = w2 / r;
    int c1 = c2 + (w2-w1*r)*C2 + (h2-h1*r)*C2*r;

    vec4 p_X = vec4(n, h1, w1, c1) + 0.5;
    vec2 p_x = convert_coord(p_X, s_X, s_x, d_x);

    float v = texture2D(X, p_x).r;

    gl_FragColor = vec4(v, 0, 0, 0);
}
"""


@WebGLDescriptorGenerator.register_handler(Depth2Space)
def depth2space(op: Depth2Space) -> List[Kernel]:
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
