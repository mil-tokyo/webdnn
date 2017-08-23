from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.operators.sgemm import Sgemm
from webdnn.backend.webgl.uniform_injector import UniformInjector


def generate_template(K):
    return FragmentShaderPreamble + """
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
        vec2 p_C = convert_position(gl_FragCoord.xy, s_c, s_C, d_C) - 0.5;
        
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
            vec2 p_A = vec2(m, k) + 0.5;
            vec2 p_B = vec2(k, n) + 0.5;

            vec2 p_a = convert_position(p_A, s_A, s_a, d_a);
            vec2 p_b = convert_position(p_B, s_B, s_b, d_b);

            v_a = texture2D(A, p_a / d_a).r;
            v_b = texture2D(B, p_b / d_b).r;

            v += v_a * v_b;
        }
        
        gl_FragColor = vec4(v, 0, 0, 0);
    }
    """.replace("%%LOOP_SIZE%%", f"{K:.1f}")


@WebGLDescriptorGenerator.register_handler(Sgemm)
def elementwise_add(op: Sgemm) -> List[Kernel]:
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
