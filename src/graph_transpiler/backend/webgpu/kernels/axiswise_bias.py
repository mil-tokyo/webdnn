from typing import List

from graph_transpiler.backend.webgpu.allocator import MemoryLayout
from graph_transpiler.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from graph_transpiler.backend.webgpu.injectors.meta_injector import MetaInjector
from graph_transpiler.backend.webgpu.kernel import Kernel, GPUSize
from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.operators.axiswise_bias import AxiswiseBias
from graph_transpiler.graph.variables.attributes.order import OrderHWNC, OrderNHWC, OrderNC

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(axiswise_bias_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(axiswise_bias_Y_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(axiswise_bias_B_offset)%%;
    const int N = %%META_LOAD(axiswise_bias_N)%%;
    const int C = %%META_LOAD(axiswise_bias_C)%%;
  
    for (int gid = index; gid < N * C; gid += num_threads) {
        int c = gid % C;
        int n = gid / C;

        float result = X[gid] + B[c];
        Y[n * C + c] = result;
    }
}
"""


def axiswise_bias(op: AxiswiseBias,
                  constants_layout: MemoryLayout,
                  variables_layout: MemoryLayout) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    b = constants_layout[op.inputs["b"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.order == OrderNC or x.variable.order == OrderNHWC or x.variable.order == OrderHWNC
    assert y.variable.shape == x.variable.shape
    assert op.parameters["axis"] == Axis.C, "[WebGPU] AxiswiseBias supports only channelwise bias."

    meta_injector = MetaInjector()
    meta_injector.register({
        "axiswise_bias_X_offset": x.offset,
        "axiswise_bias_Y_offset": y.offset,
        "axiswise_bias_B_offset": b.offset,
        "axiswise_bias_N": y.variable.size // y.variable.shape_dict[Axis.C],
        "axiswise_bias_C": y.variable.shape_dict[Axis.C],
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        meta_injector.buffer
    )

    return [kernel]
