from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.order import OrderNC, OrderCN, OrderNT, OrderNTC

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(embedding_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(embedding_Y_offset)%%;
    const float *W = data_buffer + %%META_LOAD(embedding_W_offset)%%;
    const int vocabulary = %%META_LOAD(embedding_vocabulary)%%;
    const int sequence_len = %%META_LOAD(embedding_sequence_len)%%;
    const int batch_size = %%META_LOAD(embedding_batch_size)%%;
    const int dim = %%META_LOAD(embedding_dim)%%;

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


def embedding(op: Embedding, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    w = memory_layout[op.inputs["w"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNT
    assert w.variable.order == OrderCN
    assert y.variable.order == OrderNTC

    meta_injector = MetaInjector()
    meta_injector.register({
        "embedding_X_offset": x.offset,
        "embedding_Y_offset": y.offset,
        "embedding_W_offset": w.offset,
        "embedding_vocabulary": w.variable.shape_dict[Axis.C],
        "embedding_sequence_len": x.variable.shape_dict[Axis.T],
        "embedding_batch_size": x.variable.shape_dict[Axis.N],
        "embedding_dim": w.variable.shape_dict[Axis.N]
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        meta_injector.buffer
    )

    return [kernel]
