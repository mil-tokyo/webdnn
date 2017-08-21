from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.operators.sgemm import Sgemm
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.variable import Variable


def generate_template(K):
    return """
    precision highp float;
    
    %%UNIFORM(sampler2D, A)%%;
    %%UNIFORM(sampler2D, B)%%;
    
    %%UNIFORM(vec2, s_c)%%;
    %%UNIFORM(vec2, d_C)%%;
    %%UNIFORM(vec2, s_C)%%;
    
    %%UNIFORM(vec2, d_a)%%;
    %%UNIFORM(vec2, s_a)%%;
    %%UNIFORM(vec2, s_A)%%;
    
    %%UNIFORM(vec2, d_b)%%;
    %%UNIFORM(vec2, s_b)%%;
    %%UNIFORM(vec2, s_B)%%;
    
    void main() {
        vec2 p_C = mod(floor((dot(gl_FragCoord.xy-0.5, s_c)+0.5) / s_C), d_C);
        
        float m = p_C.x;
        float n = p_C.y;
    
        float v = 0.0;
            
        for (float k = 0.0; k < %%LOOP_SIZE%%; k += 1.0) {
            float v_a = texture2D(A, (mod(floor((dot(vec2(m, k), s_A)+0.5) / s_a), d_a) + 0.5) / d_a).r;
            float v_b = texture2D(B, (mod(floor((dot(vec2(k, n), s_B)+0.5) / s_b), d_b) + 0.5) / d_b).r;
            v += v_a * v_b;
        }
        
        gl_FragColor = vec4(v, 0, 0, 0);
    }
    """.replace("%%LOOP_SIZE%%", f"{K:.1f}")


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


@WebGLDescriptorGenerator.register_handler(Sgemm)
def elementwise_add(op: Sgemm, _: MemoryLayout) -> List[Kernel]:
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()
    uniform_injector.register({
        "A": A,
        "B": B,

        "s_c": texture_stride(C),
        "d_C": [op.M, op.N],
        "s_C": [op.N, 1],

        "d_a": texture_shape(A),
        "s_a": texture_stride(A),
        "s_A": [op.K, 1] if op.transpose_A else [1, op.M],

        "d_b": texture_shape(B),
        "s_b": texture_stride(B),
        "s_B": [op.N, 1] if op.transpose_B else [1, op.K],

        "K": op.K
    })

    source = generate_template(op.K)
    source = name_injector.inject(source)
    source = uniform_injector.inject(source)

    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        C
    )

    return [kernel]
