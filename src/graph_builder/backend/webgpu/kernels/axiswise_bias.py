from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators import AxiswiseBias
from graph_builder.graph.operators.attributes import Axis

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(channelwise_bias_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(channelwise_bias_Y_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(channelwise_bias_B_offset)%%;
    const int N = %%META_LOAD(channelwise_bias_N)%%;
    const int C = %%META_LOAD(channelwise_bias_C)%%;
  
    for (int gid = index; gid < N; gid += num_threads) {
        int c = gid % C;

        float result = X[gid] + B[c];
        //Y[gid] = %%CHANNELWISE_ATTACHABLE(result, c)%%;
        Y[gid] = result;
    }
}
"""


def axiswise_bias(op: AxiswiseBias,
                  constants_layout: MemoryLayout,
                  variables_layout: MemoryLayout,
                  metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"].name]
    b = constants_layout[op.inputs["b"].name]
    y = variables_layout[op.outputs["y"].name]

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()
    metabuffer_injector.register({
        "channelwise_bias_X_offset": x.offset,
        "channelwise_bias_Y_offset": y.offset,
        "channelwise_bias_B_offset": b.offset,
        "channelwise_bias_N": y.variable.size,
        "channelwise_bias_C": y.variable.shape_dict[Axis.C],
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("channelwise_bias", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
