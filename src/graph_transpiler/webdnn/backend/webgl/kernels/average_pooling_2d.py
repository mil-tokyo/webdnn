from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def generate_template(ksize):
    return """
    precision highp float;
    
    %%UNIFORM(sampler2D, X)%%;
    
    %%UNIFORM(vec2, s_y)%%;
    %%UNIFORM(vec4, d_Y)%%;
    %%UNIFORM(vec4, s_Y)%%;
    
    %%UNIFORM(vec2, d_x)%%;
    %%UNIFORM(vec2, s_x)%%;
    %%UNIFORM(vec4, d_X)%%;
    %%UNIFORM(vec4, s_X)%%;
    
    %%UNIFORM(float, C1)%%;
    %%UNIFORM(float, H1)%%;
    %%UNIFORM(float, W1)%%;
    %%UNIFORM(float, SH)%%;
    %%UNIFORM(float, SW)%%;
    %%UNIFORM(float, PH)%%;
    %%UNIFORM(float, PW)%%;
    
    void main() {
        vec4 p_Y = mod(floor(dot(gl_FragCoord.xy-0.5, s_y) / s_Y), d_Y);
    
        float n = p_Y.x;
        float h2 = p_Y.y;
        float w2 = p_Y.z; 
        float c = p_Y.w;
    
        float sum = 0.0;
        
        for (float kh = 0.0; kh < %%KSIZE_H%%; kh += 1.0) {
            float h1 = h2 * SH - PH + kh;
            if (h1 < 0.0 || h1 >= H1) continue;
    
            for (float kw = 0.0; kw < %%KSIZE_W%%; kw += 1.0) {
                float w1 = w2 * SW - PW + kw;
                if (w1 < 0.0 || w1 >= W1) continue;

                vec4 p_X = vec4(n, h1, w1, c);
                vec2 p_x = mod(floor(dot(mod(p_X, d_X), s_X) / s_x), d_x) + 0.5;
        
                sum += texture2D(X, p_x / d_x).r;
            }
        }
        
        gl_FragColor = vec4(sum / %%KSIZE_HW%%, 0, 0, 0);
    }
    """ \
        .replace("%%KSIZE_H%%", f"{ksize[0]:.1f}") \
        .replace("%%KSIZE_W%%", f"{ksize[1]:.1f}") \
        .replace("%%KSIZE_HW%%", f"{ksize[0] * ksize[1]:.1f}")


def texture_shape(v: Variable):
    # texture_length = (v.size + 4 - 1) // 4
    texture_length = v.size
    return [
        texture_length if texture_length < 2048 else 2048,
        (texture_length + 2048 - 1) // 2048
    ]


def texture_stride(v: Variable):
    result = []
    s = 1
    for d in texture_shape(v):
        result.append(s)
        s *= d
    return result


@WebGLDescriptorGenerator.register_handler(AveragePooling2D)
def elementwise_add(op: AveragePooling2D, _: MemoryLayout) -> List[Kernel]:
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
        "d_X": x.shape,
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
