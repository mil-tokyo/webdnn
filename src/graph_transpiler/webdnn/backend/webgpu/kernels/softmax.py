from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.softmax import Softmax
from webdnn.util.misc import mul


@WebGPUDescriptorGenerator.register_handler(Softmax)
def softmax(op: Softmax, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    if x.order == y.order:
        return softmax_same_order(op, memory_layout)

    else:
        raise NotImplementedError()


template_same_order = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = %%LOAD_BUFFER(softmax_X)%%;
    device float *Y = %%LOAD_BUFFER(softmax_Y)%%;
    const int D1 = %%LOAD_BUFFER(softmax_D1)%%;
    const int D2 = %%LOAD_BUFFER(softmax_D2)%%;
    const int D3 = %%LOAD_BUFFER(softmax_D3)%%;

    for (int gid = index; gid < D1 * D3; gid += num_threads) {
        const int d3 = gid % D3;
        const int d1 = gid / D3;

        float set_max = 0.0f;
        for (int d2 = 0; d2 < D2; d2++) {
            float val = X[(d1 * D2 + d2) * D3 + d3];
            if (val > set_max) {
                set_max = val;
            }
        }

        float sum_exp = 0.0f;
        for (int d2 = 0; d2 < D2; d2++) {
            float val = X[(d1 * D2 + d2) * D3 + d3];
            float exp_x = exp(val - set_max);
            sum_exp += exp_x;
            Y[(d1 * D2 + d2) * D3 + d3] = exp_x;
        }

        for (int d2 = 0; d2 < D2; d2++) {
            Y[(d1 * D2 + d2) * D3 + d3] /= sum_exp;
        }
    }
}
"""


def softmax_same_order(op: Softmax, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    target_axis = op.parameters["axis"]
    target_axis_index = x.order.axes_dict[target_axis]
    D1 = mul(x.shape[:target_axis_index])
    D2 = x.shape[target_axis_index]
    D3 = mul(x.shape[target_axis_index + 1:])

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "softmax_X": memory_layout[x],
        "softmax_Y": memory_layout[y],
        "softmax_D1": D1,
        "softmax_D2": D2,
        "softmax_D3": D3
    })

    name_injector = KernelNameInjector(op)

    source = template_same_order
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(MAX_THREADS_PER_THREADGROUP, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
