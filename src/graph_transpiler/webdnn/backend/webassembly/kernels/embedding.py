from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.order import OrderCN, OrderNT, OrderNTC

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(embedding_X)%%;
    float *Y = %%LOAD_BUFFER(embedding_Y)%%;
    const float *W = %%LOAD_BUFFER(embedding_W)%%;
    const int vocabulary = %%LOAD_BUFFER(embedding_vocabulary)%%;
    const int sequence_len = %%LOAD_BUFFER(embedding_sequence_len)%%;
    const int batch_size = %%LOAD_BUFFER(embedding_batch_size)%%;
    const int dim = %%LOAD_BUFFER(embedding_dim)%%;

    for (int gid = 0; gid < batch_size * sequence_len; gid += 1) {
        int t = gid % sequence_len;
        int batch = gid / sequence_len;

        int word = (int)X[gid];
        for (int d = 0; d < dim; d++) {
            Y[gid * dim + d] = W[word * dim + d];
        }
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Embedding)
def embedding(op: Embedding, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    w = op.inputs["w"]
    y = op.outputs["y"]

    assert x.order == OrderNT
    assert w.order == OrderCN
    assert y.order == OrderNTC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "embedding_X": memory_layout[x],
        "embedding_Y": memory_layout[y],
        "embedding_W": memory_layout[w],
        "embedding_vocabulary": w.shape_dict[Axis.C],
        "embedding_sequence_len": x.shape_dict[Axis.T],
        "embedding_batch_size": x.shape_dict[Axis.N],
        "embedding_dim": w.shape_dict[Axis.N]
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
