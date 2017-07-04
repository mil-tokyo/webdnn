from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.threshold_relu import ThresholdRelu

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(threshold_relu_X)%%;
    float *Y = %%LOAD_BUFFER(threshold_relu_Y)%%;

    const int N = %%LOAD_BUFFER(threshold_relu_N)%%;
    const float t = *((float *)(& %%LOAD_BUFFER(threshold_relu_t)%%));
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = result < t ? 0.0 : result;
        
        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def threshold_relu(op: ThresholdRelu, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x0"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "threshold_relu_X": x,
        "threshold_relu_Y": y,
        "threshold_relu_N": y.variable.size,
        "threshold_relu_t": float(op.threshold),
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
