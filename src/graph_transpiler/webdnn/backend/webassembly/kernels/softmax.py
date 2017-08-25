from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.softmax import Softmax

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(softmax_X)%%;
    float *Y = %%LOAD_BUFFER(softmax_Y)%%;
    const int N = %%LOAD_BUFFER(softmax_N)%%;
    const int C = %%LOAD_BUFFER(softmax_C)%%;

    for (int n = 0; n < N; n++) {
        float set_max = X[n * C];
        for (int c = 0; c < C; c++) {
            float val = X[n * C + c];
            if (val > set_max) {
                set_max = val;
            }
        }

        float sum_exp = 0.0F;
        for (int c = 0; c < C; c++) {
            float val = X[n * C + c];
            float exp_x = expf(val - set_max);
            sum_exp += exp_x;
            Y[n * C + c] = exp_x;
        }

        for (int c = 0; c < C; c++) {
            Y[n * C + c] /= sum_exp;
        }
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Softmax)
def softmax(op: Softmax, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert y.order == x.order
    assert y.shape == x.shape

    axis = op.parameters["axis"]
    assert axis == x.order.axes[-1], "[Webassembly] Softmax supports only for aggregating last axis."

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "softmax_X": memory_layout[x],
        "softmax_Y": memory_layout[y],
        "softmax_N": y.size // y.shape_dict[axis],
        "softmax_C": y.shape_dict[axis],
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
