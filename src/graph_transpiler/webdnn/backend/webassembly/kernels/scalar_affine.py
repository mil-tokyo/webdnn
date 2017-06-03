from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.graph.operators.scalar_affine import ScalarAffine

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
s
        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def scalar_affine(op: ScalarAffine, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]
    assert x.variable.shape == y.variable.shape

    meta_injector = MetaInjector()
    meta_injector.register({
        "affine_transform_X_offset": x.offset,
        "affine_transform_Y_offset": y.offset,
        "affine_transform_N": y.variable.size,
        "affine_transform_scale": op.scale,
        "affine_transform_bias": op.bias
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        meta_injector.buffer
    )

    return [kernel]
