from typing import List

from graph_builder.backend.webassembly.allocator import MemoryLayout
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels import util
from graph_builder.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators.tanh import Tanh

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(relu_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(relu_Y_offset)%%;

    const int N = %%META_LOAD(relu_N)%%;
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = tanhf(result);      
        //Y[gid] = %%ELEMENTWISE_ATTACHABLE(result)%%;
        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def tanh(op: Tanh,
         constants_layout: MemoryLayout,
         variables_layout: MemoryLayout,
         metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.axis_order == y.variable.shape

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()
    metabuffer_injector.register({
        "relu_X_offset": x.offset,
        "relu_Y_offset": y.offset,
        "relu_N": y.variable.size
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("tanh", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
