from typing import List

from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.kernels import util
from webdnn.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.graph.operators.tanh import Tanh

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(relu_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(relu_Y_offset)%%;

    const int N = %%META_LOAD(relu_N)%%;
  
    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = tanhf(result);      
        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def tanh(op: Tanh,
         memory_layout: MemoryLayout,
         metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == y.variable.order
    assert x.variable.shape == y.variable.shape

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
