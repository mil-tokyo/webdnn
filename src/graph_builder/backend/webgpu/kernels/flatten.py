from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators import Flatten


# template = """
# kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
#                           device float *data_buffer[[buffer(1)]],
#                           const device int * %%META_NAME%% [[buffer(2)]],
#                           uint index[[thread_position_in_grid]],
#                           uint num_threads[[threads_per_grid]])
# {
#     const device float *x = data_buffer + %%META_LOAD(flatten_x_offset)%%;
#     device float *y = data_buffer + %%META_LOAD(flatten_y_offset)%%;
#
#     const int N = %%META_LOAD(flatten_N)%%;
#
#     for (int gid = index; gid < N; gid += num_threads) {
#         y[gid] = x[gid];
#     }
# }
# """


# noinspection PyUnusedLocal
def flatten(op: Flatten,
            constants_layout: MemoryLayout,
            variables_layout: MemoryLayout,
            metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    return []
    # x = variables_layout[op.inputs["x"]]
    # y = variables_layout[op.outputs["y"]]
    #
    # if metabuffer_injector is None:
    #     metabuffer_injector = MetaBufferInjector()
    #
    # metabuffer_injector.register({
    #     "flatten_x_offset": x.offset,
    #     "flatten_y_offset": y.offset,
    #     "flatten_N": y.variable.size,
    # })
    #
    # source = metabuffer_injector.inject(template)
    # func_name = util.add_canonical_suffix("flatten", source)
    # source = source.replace("%%FUNC_NAME%%", func_name)
    #
    # kernel = Kernel(
    #     {func_name: source},
    #     func_name,
    #     GPUSize(8, 1, 1),
    #     GPUSize(1024, 1, 1),
    #     metabuffer_injector.generate_buffer()
    # )
    #
    # return [kernel]
