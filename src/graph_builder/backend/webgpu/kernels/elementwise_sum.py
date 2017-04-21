from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators import AxiswiseScale

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X0 = data_buffer + %%META_LOAD(elementwise_sum_X0_offset)%%;
    const device float *X1 = data_buffer + %%META_LOAD(elementwise_sum_X1_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(elementwise_sum_Y_offset)%%;
    const int N = %%META_LOAD(elementwise_sum_N)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        float result = X0[gid] + X1[gid];
        //Y[gid] = %%CHANNELWISE_ATTACHABLE(result, c)%%;
        Y[gid] = result;
    }
}
"""


def elementwise_sum(op: AxiswiseScale,
                    constants_layout: MemoryLayout,
                    variables_layout: MemoryLayout,
                    metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x0 = variables_layout[op.inputs["x0"]]
    x1 = variables_layout[op.inputs["x1"]]
    y = variables_layout[op.outputs["y"]]

    assert len(op.inputs) == 2, "[WebGPU] ElementwiseSum operator currently supported only 2 inputs."

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "elementwise_sum_X0_offset": x0.offset,
        "elementwise_sum_X1_offset": x1.offset,
        "elementwise_sum_Y_offset": y.offset,
        "elementwise_sum_N": y.variable.size
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("elementwise_sum", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
