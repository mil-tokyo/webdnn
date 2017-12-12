from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.axis import Axis
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.util.misc import mul


@WebGPUDescriptorGenerator.register_handler(LocalResponseNormalization)
def local_response_normalization(op: LocalResponseNormalization, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    if x.order == y.order:
        return local_response_normalization_same_order(op, memory_layout)

    else:
        return local_response_normalization_general(op, memory_layout)


template_same_order = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = %%LOAD_BUFFER(local_response_normalization_X)%%;
    device float *Y = %%LOAD_BUFFER(local_response_normalization_Y)%%;
    const int D1 = %%LOAD_BUFFER(local_response_normalization_D1)%%;
    const int D2 = %%LOAD_BUFFER(local_response_normalization_D2)%%;
    const int D3 = %%LOAD_BUFFER(local_response_normalization_D3)%%;

    const int Phalfn = %%LOAD_BUFFER(local_response_normalization_param_half_n)%%;
    const float Pk = *((const device float *)(& %%LOAD_BUFFER(local_response_normalization_param_k)%%));
    const float Palpha = *((const device float *)(& %%LOAD_BUFFER(local_response_normalization_param_alpha)%%));
    const float Pmbeta = *((const device float *)(& %%LOAD_BUFFER(local_response_normalization_param_minus_beta)%%));

    for (int gid = index; gid < D1 * D2 * D3; gid += num_threads) {
        const int d3 = gid % D3;
        const int d2 = gid / D3 % D2;
        const int d1 = gid / D3 / D2;

        int ch_low = max(d2 - Phalfn, 0);
        int ch_high = min(d2 + Phalfn + 1, D2);

        float sq_sum = 0.0;
        for (; ch_low < ch_high; ch_low++) {
            float val = X[(d1 * D2 + ch_low) * D3 + d3];
            sq_sum += val * val;
        }

        float scale = powr(sq_sum * Palpha + Pk, Pmbeta);
        float v = X[gid] * scale;

        Y[gid] = v;
    }
}
"""


def local_response_normalization_same_order(op: LocalResponseNormalization, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    target_axis = Axis.C  # FIXME
    target_axis_index = x.order.axes_dict[target_axis]
    D1 = mul(x.shape[:target_axis_index])
    D2 = x.shape[target_axis_index]
    D3 = mul(x.shape[target_axis_index + 1:])

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "local_response_normalization_X": memory_layout[x],
        "local_response_normalization_Y": memory_layout[y],
        "local_response_normalization_D1": D1,
        "local_response_normalization_D2": D2,
        "local_response_normalization_D3": D3,
        "local_response_normalization_param_half_n": int(op.parameters["n"] // 2),
        "local_response_normalization_param_k": float(op.parameters["k"]),
        "local_response_normalization_param_alpha": float(op.parameters["alpha"]),
        "local_response_normalization_param_minus_beta": float(-op.parameters["beta"])
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


template_general = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(local_response_normalization_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(local_response_normalization_Y_offset)%%;
    const int D = %%META_LOAD(local_response_normalization_D)%%;
    const int d_target = %%META_LOAD(local_response_normalization_d_target)%%;
    const device int *x_shape = &(%%META_LOAD(local_response_normalization_x_shape)%%);
    const device int *x_stride_in_y = %(%%META_LOAD(local_response_normalization_x_stride_in_y)%%);

    const int Phalfn = %%META_LOAD(local_response_normalization_param_half_n)%%;
    const float Pk = *((const device float *)(& %%META_LOAD(local_response_normalization_param_k)%%));
    const float Palpha = *((const device float *)(& %%META_LOAD(local_response_normalization_param_alpha)%%));
    const float Pmbeta = *((const device float *)(& %%META_LOAD(local_response_normalization_param_minus_beta)%%));

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

        const int d3 = gid % D3;
        const int d2 = gid / D3 % D2;
        const int d1 = gid / D3 / D2;

        int ch_low = max(d2 - Phalfn, 0);
        int ch_high = min(d2 + Phalfn + 1, D2);

        float sq_sum = 0.0;
        for (; ch_low < ch_high; ch_low++) {
            float val = X[(d1 * D2 + ch_low) * D3 + d3];
            sq_sum += val * val;
        }

        float scale = powr(sq_sum * Palpha + Pk, Pmbeta);
        float v = X[gid] * scale;

        Y[y_offset] = v;
    }
}
"""


def local_response_normalization_general(op: LocalResponseNormalization, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    target_axis = Axis.C

    x_shape = x.shape

    y_strides = []
    stride = 1
    for s in reversed(y.shape):
        y_strides.insert(0, stride)
        stride *= s

    x_stride_in_y = [y_strides[y.order.axes_dict[axis]] for axis in x.order.axes]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "local_response_normalization_X": memory_layout[x],
        "local_response_normalization_Y": memory_layout[y],
        "local_response_normalization_D": x.ndim,
        "local_response_normalization_d_target": x.order.axes_dict[target_axis],
        "local_response_normalization_x_shape": x_shape,
        "local_response_normalization_x_stride_in_y": x_stride_in_y,
        "local_response_normalization_param_half_n": int(op.parameters["n"] // 2),
        "local_response_normalization_param_k": float(op.parameters["k"]),
        "local_response_normalization_param_alpha": float(op.parameters["alpha"]),
        "local_response_normalization_param_minus_beta": float(-op.parameters["beta"])
    })

    name_injector = KernelNameInjector(op)

    source = template_general
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
