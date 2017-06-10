from typing import List

import numpy as np

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.place_holder import PlaceHolder


def axiswise_bias(op: AxiswiseBias,
                  memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    y = memory_layout[op.outputs["y"]]

    if x.variable.order == y.variable.order:
        return axiswise_bias_same_order(op, memory_layout)

    else:
        return axiswise_bias_general(op, memory_layout)


def generate_template_same_order(D1, D3):
    return """
kernel void %%FUNC_NAME%%(device float *data_buffer[[buffer(0)]],
                          const device int * %%META_NAME%% [[buffer(1)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
#define FLAG_D1_EQUAL_1 %%FLAG_D1_EQUAL_1%%
#define FLAG_D3_EQUAL_1 %%FLAG_D3_EQUAL_1%%

    const device float *X = data_buffer + %%META_LOAD(axiswise_bias_X_offset)%%;
    const device float *B = data_buffer + %%META_LOAD(axiswise_bias_B_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(axiswise_bias_Y_offset)%%;

#if !OPTIMIZE || !FLAG_D1_EQUAL_1
    const int D1 = %%META_LOAD(axiswise_bias_D1)%%;
#endif

    const int D2 = %%META_LOAD(axiswise_bias_D2)%%;

#if !OPTIMIZE || !FLAG_D3_EQUAL_1
    const int D3 = %%META_LOAD(axiswise_bias_D3)%%;
#endif

#if OPTIMIZE && FLAG_D3_EQUAL_1
    #if OPTIMIZE && FLAG_D1_EQUAL_1
        for (int gid = index; gid < D2; gid += num_threads) {
            const int d2 = gid;
    #else
        for (int gid = index; gid < D1 * D2; gid += num_threads) {
            const int d2 = gid % D2;
    #endif

#else

    #if OPTIMIZE && FLAG_D1_EQUAL_1
        for (int gid = index; gid < D2 * D3; gid += num_threads) {
            const int d2 = gid / D3 % D2;
    
    #else
        for (int gid = index; gid < D1 * D2 * D3; gid += num_threads) {
            const int d2 = gid / D3 % D2;
    #endif

#endif

        float v = X[gid] + B[d2];

        Y[gid] = v;
    }

#undef FLAG_D1_EQUAL_1
#undef FLAG_D3_EQUAL_1
}
""" \
        .replace("%%FLAG_D1_EQUAL_1%%", "1" if D1 == 1 else "0") \
        .replace("%%FLAG_D3_EQUAL_1%%", "1" if D3 == 1 else "0")


def axiswise_bias_same_order(op: AxiswiseBias,
                             memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    b = memory_layout[op.inputs["b"]]
    y = memory_layout[op.outputs["y"]]

    target_axis_index = x.variable.order.axes_dict[op.axis]
    D1 = np.product(x.variable.shape[:target_axis_index])
    D2 = x.variable.shape[target_axis_index]
    D3 = np.product(x.variable.shape[target_axis_index + 1:])

    meta_injector = MetaInjector()
    meta_injector.register({
        "axiswise_bias_X_offset": x.offset,
        "axiswise_bias_B_offset": b.offset,
        "axiswise_bias_Y_offset": y.offset,
        "axiswise_bias_D1": D1,
        "axiswise_bias_D2": D2,
        "axiswise_bias_D3": D3
    })

    name_injector = KernelNameInjector(op)

    source = generate_template_same_order(D1, D3)
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


template_general = """
kernel void %%FUNC_NAME%%(device float *data_buffer[[buffer(0)]],
                          const device int * %%META_NAME%% [[buffer(1)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(axiswise_bias_X_offset)%%;
    const device float *B = data_buffer + %%META_LOAD(axiswise_bias_B_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(axiswise_bias_Y_offset)%%;
    const int D = %%META_LOAD(axiswise_bias_D)%%;
    const int d_target = %%META_LOAD(axiswise_bias_d_target)%%;
    const device int *x_shape = &(%%META_LOAD(axiswise_bias_x_shape)%%);
    const device int *x_stride_in_y = &(%%META_LOAD(axiswise_bias_x_stride_in_y)%%);

    int size = 1;
    for (int d = 0; d < D; d++) size *= x_shape[d];

    int D1 = 1;
    for (int d = 0; d < d_target; d++) D1 *= x_shape[d];

    const int D2 = x_shape[d_target];

    int D3 = 1;
    for (int d = d_target + 1; d < D; d++) D3 *= x_shape[d];

    for (int gid = index; gid < size; gid += num_threads) {

        int y_offset = 0;
        int s = gid;
        for (int d = D - 1; d >= 0; d--) {
            y_offset += x_stride_in_y[d] * (s % x_shape[d]);
            s /= x_shape[d];
        }

        const int d2 = gid / D3 % D2;

        float v = X[gid] + B[d2];

        Y[y_offset] = v;
    }
}
"""


def axiswise_bias_general(op: AxiswiseBias,
                          memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    b = memory_layout[op.inputs["b"]]
    y = memory_layout[op.outputs["y"]]

    x_shape = x.variable.shape

    y_strides = []
    stride = 1
    for s in reversed(y.variable.shape):
        y_strides.insert(0, stride)
        stride *= s

    x_stride_in_y = [y_strides[y.variable.order.axes_dict[axis]] for axis in x.variable.order.axes]

    meta_injector = MetaInjector()
    meta_injector.register({
        "axiswise_bias_X_offset": x.offset,
        "axiswise_bias_B_offset": b.offset,
        "axiswise_bias_Y_offset": y.offset,
        "axiswise_bias_D": x.variable.ndim,
        "axiswise_bias_d_target": x.variable.order.axes_dict[op.axis],
        "axiswise_bias_x_shape": np.array(x_shape, dtype=np.int32).tobytes(),
        "axiswise_bias_x_stride_in_y": np.array(x_stride_in_y, dtype=np.int32).tobytes(),
    })

    name_injector = KernelNameInjector(op)

    source = template_general
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
