from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.operators.unpooling_2d import Unpooling2D
from webdnn.graph.order import OrderNHWC


def generate_template(ksize):
    return FragmentShaderPreamble + """
    %%UNIFORM(sampler2D, X)%%;

    %%UNIFORM(vec2, s_y)%%;
    %%UNIFORM(vec4, d_Y)%%;
    %%UNIFORM(vec4, s_Y)%%;

    %%UNIFORM(vec2, d_x)%%;
    %%UNIFORM(vec2, s_x)%%;
    %%UNIFORM(vec4, s_X)%%;

    %%UNIFORM(int, C1)%%;
    %%UNIFORM(int, H1)%%;
    %%UNIFORM(int, W1)%%;
    %%UNIFORM(int, SH)%%;
    %%UNIFORM(int, SW)%%;
    %%UNIFORM(int, PH)%%;
    %%UNIFORM(int, PW)%%;

    void main() {
        ivec4 p_Y = convert_position_i(gl_FragCoord.xy, s_y, s_Y, d_Y);
        int n = p_Y.x;
        int h2 = p_Y.y;
        int w2 = p_Y.z;
        int c = p_Y.w;

        float sum = 0.0;

        for (int kh = 0; kh < %%KSIZE_H%%; kh++) {
            int h1 = h2 + PH - kh;
            if (h1 < 0 || h1 >= H1 * SH) continue;
            int mod_sh = h1 - h1 / SH * SH;
            if (mod_sh != 0) continue;
            h1 /= SH;
            for (int kw = 0; kw < %%KSIZE_W%%; kw++) {
                int w1 = w2 + PW - kw;
                if (w1 < 0 || w1 >= W1 * SW) continue;
                int mod_sw = w1 - w1 / SW * SW;
                if (mod_sw != 0) continue;
                w1 /= SW;

                sum += texture2D(X, convert_coord(vec4(n, h1, w1, c) + 0.5, s_X, s_x, d_x)).r;
            }
        }

        gl_FragColor = vec4(sum, 0, 0, 0);
    }
    """ \
        .replace("%%KSIZE_H%%", f"{ksize[0]}") \
        .replace("%%KSIZE_W%%", f"{ksize[1]}")


@WebGLDescriptorGenerator.register_handler(Unpooling2D)
def average_pooling_2d(op: Unpooling2D) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

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
        "s_X": x.stride,

        "C1": x.shape_dict[Axis.C],
        "H1": x.shape_dict[Axis.H],
        "W1": x.shape_dict[Axis.W],
        "SH": op.parameters["stride"][0],
        "SW": op.parameters["stride"][1],
        "PH": op.parameters["padding"][0],
        "PW": op.parameters["padding"][1],
    })

    source = generate_template(ksize=op.parameters["ksize"])
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
