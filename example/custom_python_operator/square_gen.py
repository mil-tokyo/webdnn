import os
from typing import List, Optional

from square import SquareLayer
from webdnn.graph.variable import Variable

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.operator import Operator

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNC
from webdnn.graph.custom_python_operator.generator import generate_wasm_src


@KerasConverter.register_handler("SquareLayer")
def square_converter_handler(converter: KerasConverter, keras_layer: SquareLayer):
    keras_x = converter.get_input_tensor(keras_layer)[0]
    keras_y = converter.get_output_tensor(keras_layer)[0]

    webdnn_x = converter.get_variable(keras_x)

    # at this point, they are placeholder
    # assert webdnn_x.order == OrderNC
    # assert keras_x.shape == keras_y.shape
    webdnn_x.order.unify(OrderNC)
    webdnn_operator = SquareLayerOperator(None, webdnn_x.shape, webdnn_x.order)

    webdnn_y, = webdnn_operator(webdnn_x)

    converter.set_variable(keras_y, webdnn_y)


class SquareLayerOperator(Operator):
    def __init__(self, name: Optional[str], output_shape, output_order):
        super().__init__(name)
        self.output_shape = output_shape
        self.output_order = output_order

    def __call__(self, x: Variable):
        y = Variable(self.output_shape, self.output_order)

        self.append_input("x", x)
        self.append_output("y", y)
        return y,


template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(cpo_X)%%;
    float *Y = %%LOAD_BUFFER(cpo_Y)%%;
    const int N = %%LOAD_BUFFER(cpo_N)%%;
    const int C = %%LOAD_BUFFER(cpo_C)%%;

    int x_shape[2] = {N, C};
    int shape[2] = {N, C};
    for (int gid = 0; gid < N * C; gid += 1) {
        const int c = gid % C;
        const int n = gid / C;
        int pos[2] = {n, c};
        
        Y[gid] = %%FUNC_NAME%%_element(shape, pos, x_shape, X);
    }
}
"""


def generate_element_kernel_source():
    return generate_wasm_src(os.path.join(os.path.dirname(__name__), "square_impl.py"))


@WebassemblyDescriptorGenerator.register_handler(SquareLayerOperator)
def webassembly_square_layer(op: SquareLayerOperator, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order == OrderNC, x.order
    assert y.order == OrderNC, y.order

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "cpo_X": memory_layout[x],
        "cpo_Y": memory_layout[y],
        "cpo_N": x.shape_dict[Axis.N],
        "cpo_C": x.shape_dict[Axis.C],
    })

    name_injector = KernelNameInjector(op)

    source = generate_element_kernel_source() + template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
