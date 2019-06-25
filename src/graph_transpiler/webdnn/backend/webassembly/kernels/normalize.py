from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.normalize import Normalize

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(normalize_X)%%;
    float *Y = %%LOAD_BUFFER(normalize_Y)%%;
    const int N = %%LOAD_BUFFER(normalize_N)%%;
    const int C = %%LOAD_BUFFER(normalize_C)%%;
    const float eps = *((const float *)(& %%LOAD_BUFFER(normalize_param_eps)%%));

    for (int n = 0; n < N; n++) {
        float sq_sum = 0.0F;
        for (int c = 0; c < C; c++) {
            float val = X[n * C + c];
            sq_sum += val * val;
        }

        sq_sum = 1.0F / (sqrt(sq_sum) + eps);

        for (int c = 0; c < C; c++) {
            float val = X[n * C + c];
            Y[n * C + c] = val * sq_sum;
        }
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Normalize)
def Normalize(op: Normalize, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert y.order == x.order
    assert y.shape == x.shape

    axis = op.parameters["axis"]
    assert axis == x.order.axes[-1], "[Webassembly] Normalize supports only for aggregating last axis."

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "normalize_X": memory_layout[x],
        "normalize_Y": memory_layout[y],
        "normalize_N": y.size // y.shape_dict[axis],
        "normalize_C": y.shape_dict[axis],
        "normalize_param_eps": float(op.parameters["eps"]),
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
