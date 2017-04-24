from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import GPUSize, Kernel
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators.relu import Relu

template = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(relu_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(relu_Y_offset)%%;

    const int N = %%META_LOAD(relu_N)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        float result = X[gid];
        result = result < 0.0 ? 0.0 : result;      
        //Y[gid] = %%ELEMENTWISE_ATTACHABLE(result)%%;
        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def relu(op: Relu,
         constants_layout: MemoryLayout,
         variables_layout: MemoryLayout,
         metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.shape == y.variable.shape

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()
    metabuffer_injector.register({
        "relu_X_offset": x.offset,
        "relu_Y_offset": y.offset,
        "relu_N": y.variable.size
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("relu", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
