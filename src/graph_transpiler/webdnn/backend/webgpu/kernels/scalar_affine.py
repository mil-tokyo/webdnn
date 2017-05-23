from typing import List

from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.backend.webgpu.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.graph.operators.scalar_affine import ScalarAffine

template = """
kernel void %%FUNC_NAME%%(const device float *param_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(affine_transform_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(affine_transform_Y_offset)%%;

    const float scale = *((const device float *)(& %%META_LOAD(affine_transform_scale)%%));
    const float bias = *((const device float *)(& %%META_LOAD(affine_transform_bias)%%));
    const int N = %%META_LOAD(affine_transform_N)%%;

    for (int gid = index; gid < N; gid += num_threads) {
        float result = X[gid];
        result = result * scale + bias;
        Y[gid] = result;
    }
}
"""


def scalar_affine(op: ScalarAffine,
                  constants_layout: MemoryLayout,
                  variables_layout: MemoryLayout) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]
    assert x.variable.shape == y.variable.shape

    meta_injector = MetaInjector()
    meta_injector.register({
        "affine_transform_X_offset": x.offset,
        "affine_transform_Y_offset": y.offset,
        "affine_transform_N": y.variable.size,
        "affine_transform_scale": float(op.scale),
        "affine_transform_bias": float(op.bias)
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
