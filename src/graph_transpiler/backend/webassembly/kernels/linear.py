from typing import List

from graph_transpiler.backend.webassembly.kernel import Kernel
from graph_transpiler.backend.webassembly.kernels import util
from graph_transpiler.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_transpiler.backend.webgpu.allocator import MemoryLayout
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.operators.linear import Linear
from graph_transpiler.graph.variables.attributes.order import OrderNC, OrderNHWC, OrderCN, OrderHWCN

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(linear_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(linear_Y_offset)%%;
    const float *W = weight_buffer + %%META_LOAD(linear_W_offset)%%;
    const int M = %%META_LOAD(linear_M)%%;
    const int N = %%META_LOAD(linear_N)%%;
    const int K = %%META_LOAD(linear_K)%%;
    
    //%%INITIALIZER_ATTACHABLE_PLACEHOLDER%%
  
    for (int gid = 0; gid < M * N; gid += 1) {
        int n = gid % N;
        int m = gid / N;

        float sum = 0.0;
        for (int k = 0; k < K; k++) {
            sum += X[m * K + k] * W[k * N + n];
        }

        //Y[gid] = %%CHANNELWISE_ATTACHABLE(sum, n)%%;
        Y[gid] = sum;
    }
}
"""


def linear(op: Linear,
           constants_layout: MemoryLayout,
           variables_layout: MemoryLayout,
           metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    w = constants_layout[op.inputs["w"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.order == OrderNC or x.variable.order == OrderNHWC
    assert w.variable.order == OrderCN or w.variable.order == OrderHWCN
    assert y.variable.order == OrderNC or y.variable.order == OrderNHWC
    assert w.variable.ndim == x.variable.ndim

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()
    metabuffer_injector.register({
        "linear_X_offset": x.offset,
        "linear_Y_offset": y.offset,
        "linear_W_offset": w.offset,
        "linear_M": y.variable.shape_dict[Axis.N],
        "linear_N": y.variable.size // y.variable.shape_dict[Axis.N],
        "linear_K": x.variable.size // x.variable.shape_dict[Axis.N],
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("linear", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
