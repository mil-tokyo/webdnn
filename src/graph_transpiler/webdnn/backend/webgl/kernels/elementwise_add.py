from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.elementwise_add import ElementwiseAdd

template = """
precision mediump float;

%%UNIFORM(float, W)%%;
%%UNIFORM(float, H)%%;
%%UNIFORM(sampler2D, X0)%%;
%%UNIFORM(sampler2D, X1)%%;

void main() {
    int x = int(gl_FragCoord.x - 0.5);
    int y = int(gl_FragCoord.y - 0.5);
    int index = y * int(W) + x; 
    
    vec2 pos0 = vec2(float(x) / W, float(y) / H);
    vec2 pos1 = vec2(float(x) / W, float(y) / H);
    
    float v0 = texture2D(X0, pos0).r;
    float v1 = texture2D(X1, pos1).r;
    
    gl_FragColor = vec4(v0 + v1, 0, 0, 0);
}
"""


@WebGLDescriptorGenerator.register_handler(ElementwiseAdd)
def elementwise_add(op: ElementwiseAdd, memory_layout: MemoryLayout) -> List[Kernel]:
    x0 = memory_layout[op.inputs["x0"]]
    x1 = memory_layout[op.inputs["x1"]]
    y = memory_layout[op.outputs["y"]]

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()
    uniform_injector.register({
        "X0": x0.variable,
        "X1": x1.variable,
        "W": y.size,
        "H": 1
    })

    source = template
    source = name_injector.inject(source)
    source = uniform_injector.inject(source)

    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        y.variable
    )

    return [kernel]
