from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWCN

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_index_in_threadgroup]],
                          uint2 group_position[[threadgroup_position_in_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(sgemm_X_offset)%%;
    const device float *W = weight_buffer + %%META_LOAD(sgemm_W_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(sgemm_B_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(sgemm_Y_offset)%%;

    const int M = %%META_LOAD(sgemm_M)%%;
    const int N = %%META_LOAD(sgemm_N)%%;
    const int K = %%META_LOAD(sgemm_K)%%;

    const int m_tile_offset = group_position.x;
    const int n_tile_offset = group_position.y;
    const int m_offset = index % 8;
    const int n_offset = index / 8;

    threadgroup float shared[64 * 8 * 2 * 2];

    const device float *load_target1 = (index >= 32) ? W : X;
    const int ldx = (index >= 32) ? N : 1;
    int track0 = (index >= 32) ? (n_tile_offset * 64 + index - 32) : ((m_tile_offset * 64 + index) * K);
    int track1 = (index >= 32) ? (track0 + 32) : (track0 + 32 * K);
    bool flag0 = (index >= 32) ? ((n_tile_offset * 64 + index - 32) >= N) : (m_tile_offset * 64 + index >= M);
    bool flag1 = (index >= 32) ? ((n_tile_offset * 64 + index) >= N) : (m_tile_offset * 64 + index + 32 >= M);
    int shared_offset = (index >= 32) ? (index + 32) : index;
    int read_X_offset = m_offset * 8;
    int read_W_offset = n_offset * 8 + 64;

    float result[64];

#pragma unroll 64
    for (int i = 0; i < 64; i++)
        result[i] = 0;

    for (int k = 0; k < K; k += 8)
    {
//Load data
#pragma unroll 8
        for (int k_sub = 0; k_sub < 8; k_sub++)
        {
            shared[shared_offset + k_sub * 128 + 32 * 0] = (k + k_sub >= K || flag0) ? 0 : load_target1[track0 + k_sub * ldx];
            shared[shared_offset + k_sub * 128 + 32 * 1] = (k + k_sub >= K || flag1) ? 0 : load_target1[track1 + k_sub * ldx];
        }

        //sync all threads in threadgroup
        threadgroup_barrier(mem_flags::mem_none);

#pragma unroll 8
        for (int k_sub = 0; k_sub < 8; k_sub++)
        {
            float x[8];
            float w[8];

#pragma unroll 8
            for (int i = 0; i < 8; i++)
            {
                x[i] = shared[read_X_offset + k_sub * 128 + i];
                w[i] = shared[read_W_offset + k_sub * 128 + i];
            }

#pragma unroll 8
            for (int m_sub = 0; m_sub < 8; m_sub++)
            {

#pragma unroll 8
                for (int n_sub = 0; n_sub < 8; n_sub++)
                {
                    result[n_sub * 8 + m_sub] += x[m_sub] * w[n_sub];
                }
            }
        }

        shared_offset ^= 64 * 8 * 2;
        read_X_offset ^= 64 * 8 * 2;
        read_W_offset ^= 64 * 8 * 2;
        track0 += ldx * 8;
        track1 += ldx * 8;
    }

    
    threadgroup_barrier(mem_flags::mem_none);

    shared[index] = (n_tile_offset * 64 + index >= N) ? 0 : B[n_tile_offset * 64 + index];

    threadgroup_barrier(mem_flags::mem_none);
    
    float b[8];
    
#pragma unroll 8
    for (int n_sub = 0; n_sub < 8; n_sub++)
    {
        b[n_sub] = shared[n_offset * 8 + n_sub];
    }

#pragma unroll 8
    for (int m_sub = 0; m_sub < 8; m_sub++)
    {
        const int mm = m_tile_offset * 64 + m_offset * 8 + m_sub;
        if (mm >= M)
            continue;

#pragma unroll 8
        for (int n_sub = 0; n_sub < 8; n_sub++)
        {
            const int nn = n_tile_offset * 64 + n_offset * 8 + n_sub;
            if (nn >= N)
                continue;

            float v = result[n_sub * 8 + m_sub] + b[n_sub];
            Y[mm * N + nn] = v > 0 ? v : 0;
        }
    }
}
"""


def sgemm_bias_relu(op: Operator,
                    constants_layout: MemoryLayout,
                    variables_layout: MemoryLayout,
                    metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    w = constants_layout[op.inputs["w"]]
    b = constants_layout[op.inputs["b"]]
    y = variables_layout[op.outputs["y"]]

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    assert x.variable.axis_order == OrderNHWC
    assert w.variable.axis_order == OrderHWCN
    assert y.variable.axis_order == OrderNHWC

    M = y.variable.shape_dict[Axis.N] * y.variable.shape_dict[Axis.H] * y.variable.shape_dict[Axis.W]
    N = w.variable.shape_dict[Axis.N]
    K = x.variable.shape_dict[Axis.C]

    metabuffer_injector.register({
        "sgemm_X_offset": x.offset,
        "sgemm_W_offset": w.offset,
        "sgemm_B_offset": b.offset,
        "sgemm_Y_offset": y.offset,
        "sgemm_M": M,
        "sgemm_N": N,
        "sgemm_K": K
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("sgemm_bias_relu", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize((M + 64 - 1) // 64, (N + 64 - 1) // 64, 1),
        GPUSize(8, 8, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
