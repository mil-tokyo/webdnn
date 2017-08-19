from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.graph.operators.elementwise_mul import ElementwiseMul

template = """
precision mediump float;
uniform float _W;
uniform float _H;
uniform sampler2D X0;
uniform sampler2D X1;

void main() {
  float x = (gl_FragCoord.x - 0.5) / _W;
  float y = (gl_FragCoord.y - 0.5) / _H;

  gl_FragColor = vec4(texture2D(X0, vec2(x, y)).r * texture2D(X1, vec2(x, y)).r, 0, 0, 0);
}
"""


@WebGLDescriptorGenerator.register_handler(ElementwiseMul)
def elementwise_mul(op: ElementwiseMul, memory_layout: MemoryLayout) -> List[Kernel]:
    x0 = memory_layout[op.inputs["x0"]]
    x1 = memory_layout[op.inputs["x1"]]
    y = memory_layout[op.outputs["y"]]

    name_injector = KernelNameInjector(op)
    source = template
    source = name_injector.inject(source)

    kernel = Kernel(
        source,
        name_injector.name,
        {"X0": x0.variable, "X1": x1.variable},
        y.variable
    )

    return [kernel]
