from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.arg_max import ArgMax

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(argmax_X)%%;
    float *Y = %%LOAD_BUFFER(argmax_Y)%%;
    const int *y_stride = %%LOAD_BUFFER(argmax_y_stride)%%;
    const int *y_shape = %%LOAD_BUFFER(argmax_y_shape)%%;
    const int *x_stride = %%LOAD_BUFFER(argmax_x_stride)%%;
    const int D = %%LOAD_BUFFER(argmax_D)%%;
    const int N = %%LOAD_BUFFER(argmax_N)%%;
    const int MAX_GID = %%LOAD_BUFFER(argmax_MAX_GID)%%;
    const int x_target_axis_stride = %%LOAD_BUFFER(argmax_x_target_axis_stride)%%;

    for (int gid = 0; gid < MAX_GID; gid++) {
        int x_index = 0;
        for (int d = 0; d < D; d++) x_index += ((gid / y_stride[d]) % y_shape[d]) * x_stride[d];

        int max_i = 0;
        float max_x = -1.0e10;
        for (int i = 0; i < N; i++) {
            const float x = X[x_index];

            if (x > max_x) {
                max_x = x;
                max_i = i;
            }

            x_index += x_target_axis_stride;
        }

        Y[gid] = (float)max_i;
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(ArgMax)
def arg_max_handler(op: ArgMax, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    axis = op.parameters["axis"]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "argmax_X": memory_layout[x],
        "argmax_Y": memory_layout[y],
        "argmax_y_stride": y.stride,
        "argmax_y_shape": y.shape,
        "argmax_x_stride": [x.stride_dict[a] for a in y.order.axes],
        "argmax_D": y.ndim,
        "argmax_N": x.shape_dict[axis],
        "argmax_MAX_GID": y.size,
        "argmax_x_target_axis_stride": x.stride_dict[axis]
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
