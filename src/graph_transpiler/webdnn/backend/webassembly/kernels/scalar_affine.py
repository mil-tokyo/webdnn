from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.operators.scalar_affine import ScalarAffine

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(affine_transform_X)%%;
    float *Y = %%LOAD_BUFFER(affine_transform_Y)%%;

    const float scale = *((const float *)(& %%LOAD_BUFFER(affine_transform_scale)%%));
    const float bias = *((const float *)(& %%LOAD_BUFFER(affine_transform_bias)%%));
    const int N = %%LOAD_BUFFER(affine_transform_N)%%;

    for (int gid = 0; gid < N; gid += 1) {
        float result = X[gid];
        result = result * scale + bias;

        Y[gid] = result;
    }
}
"""


# noinspection PyUnusedLocal
def scalar_affine(op: ScalarAffine, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x0"]]
    y = memory_layout[op.outputs["y"]]
    assert x.variable.shape == y.variable.shape

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "affine_transform_X": x,
        "affine_transform_Y": y,
        "affine_transform_N": y.variable.size,
        "affine_transform_scale": float(op.scale),
        "affine_transform_bias": float(op.bias)
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
