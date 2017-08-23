from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
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
    
    %%UNIFORM(float, C1)%%;
    %%UNIFORM(float, H1)%%;
    %%UNIFORM(float, W1)%%;
    %%UNIFORM(float, SH)%%;
    %%UNIFORM(float, SW)%%;
    %%UNIFORM(float, PH)%%;
    %%UNIFORM(float, PW)%%;
    
    void main() {
        vec4 p_Y = convert_position(gl_FragCoord.xy, s_y, s_Y, d_Y) - 0.5;    
    
        float n = p_Y.x;
        float h2 = p_Y.y;
        float w2 = p_Y.z; 
        float c = p_Y.w;
    
        float v = -1e10;
        
        // NOTE(Kiikurage): In FireFox, for-loop with incremental counter generate wrong result
        // (Maybe there're a bug in implementation of loop-unrolling optimization phase).
        //
        // Therefore, loop counter must be decremented!!
        //
        // I observed this bug in follow version of FF:
        //   (navigator.userAgent)="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0"

        for (float kh = %%KSIZE_H%% - 1.0; kh >= 0.0; kh -= 1.0) {
            float h1 = h2 * SH - PH + kh;
            if (h1 < 0.0 || h1 >= H1) continue;
    
            for (float kw = %%KSIZE_W%% - 1.0; kw >= 0.0; kw -= 1.0) {
                float w1 = w2 * SW - PW + kw;
                if (w1 < 0.0 || w1 >= W1) continue;

                vec4 p_X = vec4(n, h1, w1, c) + 0.5;
                vec2 p_x = convert_position(p_X, s_X, s_x, d_x);
        
                v = max(texture2D(X, p_x / d_x).r, v);
            }
        }
        
        gl_FragColor = vec4(v, 0, 0, 0);
    }
    """ \
        .replace("%%KSIZE_H%%", f"{ksize[0]:.1f}") \
        .replace("%%KSIZE_W%%", f"{ksize[1]:.1f}")


@WebGLDescriptorGenerator.register_handler(MaxPooling2D)
def elementwise_add(op: MaxPooling2D) -> List[Kernel]:
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
