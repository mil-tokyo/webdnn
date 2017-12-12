from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.tile import Tile

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(tile_x)%%;
    float *Y = %%LOAD_BUFFER(tile_y)%%;
    const int *y_stride = %%LOAD_BUFFER(tile_y_stride)%%;
    const int *x_stride = %%LOAD_BUFFER(tile_x_stride)%%;
    const int *x_shape = %%LOAD_BUFFER(tile_x_shape)%%;
    const int D = %%LOAD_BUFFER(tile_D)%%;
    const int MAX_GID = %%LOAD_BUFFER(tile_MAX_GID)%%;

    for (int gid = 0; gid < MAX_GID; gid ++) {
        int i = 0;
        for (int d = 0; d < D; d++) i += ((gid / y_stride[d]) % x_shape[d]) * x_stride[d];

        Y[gid] = X[i];
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Tile)
def tile(op: Tile, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "tile_x": memory_layout[x],
        "tile_y": memory_layout[y],
        "tile_y_stride": y.stride,
        "tile_x_stride": [x.stride_dict[a] for a in y.order.axes],
        "tile_x_shape": [x.shape_dict[a] for a in y.order.axes],
        "tile_D": x.ndim,
        "tile_MAX_GID": y.size,
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
