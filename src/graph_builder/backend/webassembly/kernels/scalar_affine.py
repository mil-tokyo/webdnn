from typing import List

from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels import util
from graph_builder.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.graph.operators.scalar_affine import ScalarAffine

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(affine_transform_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(affine_transform_Y_offset)%%;

    const float scale = *((const float *)(& %%META_LOAD(affine_transform_scale)%%));
    const float bias = *((const float *)(& %%META_LOAD(affine_transform_bias)%%));
    const int N = %%META_LOAD(affine_transform_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = result * scale + bias;
        //Y[gid] = %%ELEMENTWISE_ATTACHABLE(result)%%;
        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def scalar_affine(op: ScalarAffine,
                  constants_layout: MemoryLayout,
                  variables_layout: MemoryLayout,
                  metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]
    assert x.variable.shape == y.variable.shape

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()
    metabuffer_injector.register({
        "affine_transform_X_offset": x.offset,
        "affine_transform_Y_offset": y.offset,
        "affine_transform_N": y.variable.size,
        "affine_transform_scale": op.scale,
        "affine_transform_bias": op.bias
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("scalar_affine", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
