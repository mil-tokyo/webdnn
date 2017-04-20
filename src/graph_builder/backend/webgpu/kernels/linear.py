from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators import Linear
from graph_builder.graph.operators.attributes import Axis
from graph_builder.graph.variables import attributes as VA

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(linear_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(linear_Y_offset)%%;
    const device float *W = weight_buffer + %%META_LOAD(linear_W_offset)%%;
    const int M = %%META_LOAD(linear_M)%%;
    const int N = %%META_LOAD(linear_N)%%;
    const int K = %%META_LOAD(linear_K)%%;
    
    //%%INITIALIZER_ATTACHABLE_PLACEHOLDER%%
  
    for (int gid = index; gid < M * N; gid += num_threads) {
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

    assert x.variable.axis_order == VA.OrderNC \
           or x.variable.axis_order == VA.OrderNHWC, \
        f"[WebGPU] Linear operator supports OrderNC or OrderNHWC as data order of input variable. " + \
        f"Actual data order is {x.variable.axis_order.name}"
    assert w.variable.axis_order == VA.OrderCN \
           or w.variable.axis_order == VA.OrderHWCN, \
        f"[WebGPU] Linear operator supports OrderCN or OrderCHWN as data order of filter variable. " + \
        f"Actual data order is {w.variable.axis_order.name}"
    assert w.variable.ndim == x.variable.ndim, \
        "[WebGPU] Input and Filter variables of Linear operator must be same number of dimension. " + \
        f"Actual number of dimension is: x.ndim={x.variable.ndim}, w.ndim={w.variable.ndim}"

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()
    metabuffer_injector.register({
        "linear_X_offset": x.offset,
        "linear_Y_offset": y.offset,
        "linear_W_offset": w.offset,
        "linear_M": y.variable.shape_dict[Axis.N],
        "linear_N": y.variable.shape_dict[Axis.C],
        "linear_K": x.variable.shape_dict[Axis.C],
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("linear", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
