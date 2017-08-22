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
        vec2 p_c = gl_FragCoord.xy - 0.5;
        vec2 p_C = mod(floor((dot(p_c, s_c) + 0.5) / s_C) + 0.5, d_C) - 0.5;
        
        float m = p_C.x;
        float n = p_C.y;
    
        float v = 0.0;
        float v_a;
        float v_b;
        
        // NOTE(Kiikurage): In FireFox, for-loop with incremental counter generate wrong result
        // (Maybe there're a bug in implementation of loop-unrolling optimization phase).
        //
        // Therefore, loop counter must be decremented!!
        //
        // I observed this bug in follow version of FF:
        //   (navigator.userAgent)="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) Gecko/20100101 Firefox/54.0"

        for (float k = %%LOOP_SIZE%% - 1.0; k >= 0.0; k -= 1.0) {
            vec2 p_A = vec2(m, k);
            vec2 p_B = vec2(k, n);

            vec2 p_a = mod(floor((dot(p_A, s_A) + 0.5) / s_a) + 0.5, d_a) - 0.5;
            vec2 p_b = mod(floor((dot(p_B, s_B) + 0.5) / s_b) + 0.5, d_b) - 0.5;

            v_a = texture2D(A, (p_a + 0.5) / d_a).r;
            v_b = texture2D(B, (p_b + 0.5) / d_b).r;

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
