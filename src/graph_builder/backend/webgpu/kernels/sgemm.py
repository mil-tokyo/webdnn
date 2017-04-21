from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.sgemm import Sgemm
from graph_builder.graph.axis import Axis
from graph_builder.graph.variables.attributes.order import OrderNHWC, OrderHWCN

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_index_in_threadgroup]],
                          uint2 group_position[[threadgroup_position_in_grid]])
{
    const device float *A = data_buffer + %%META_LOAD(sgemm_A_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(sgemm_B_offset)%%;
    device float *C = data_buffer + %%META_LOAD(sgemm_C_offset)%%;

    const int M = %%META_LOAD(sgemm_M)%%;
    const int N = %%META_LOAD(sgemm_N)%%;
    const int K = %%META_LOAD(sgemm_K)%%;

    const int m_tile_offset = group_position.x;
    const int n_tile_offset = group_position.y;
    const int m_offset = index % 8;
    const int n_offset = index / 8;

    threadgroup float shared[64 * 8 * 2 * 2];

    const device float *load_target = (index >= 32) ? B : A;
    const int ldx = (index >= 32) ? N : 1;
    int track0 = (index >= 32) ? (n_tile_offset * 64 + index - 32) : ((m_tile_offset * 64 + index) * K);
    int track1 = (index >= 32) ? (track0 + 32) : (track0 + 32 * K);
    bool flag0 = (index >= 32) ? ((n_tile_offset * 64 + index - 32) >= N) : (m_tile_offset * 64 + index >= M);
    bool flag1 = (index >= 32) ? ((n_tile_offset * 64 + index) >= N) : (m_tile_offset * 64 + index + 32 >= M);
    int shared_offset = (index >= 32) ? (index + 32) : index;
    int read_A_offset = m_offset * 8;
    int read_B_offset = n_offset * 8 + 64;

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
            shared[shared_offset + k_sub * 128 + 32 * 0] = (k + k_sub >= K || flag0) ? 0 : load_target[track0 + k_sub * ldx];
            shared[shared_offset + k_sub * 128 + 32 * 1] = (k + k_sub >= K || flag1) ? 0 : load_target[track1 + k_sub * ldx];
        }

        //sync all threads in threadgroup
        threadgroup_barrier(mem_flags::mem_none);

#pragma unroll 8
        for (int k_sub = 0; k_sub < 8; k_sub++)
        {
            float a[8];
            float b[8];

#pragma unroll 8
            for (int i = 0; i < 8; i++)
            {
                a[i] = shared[read_A_offset + k_sub * 128 + i];
                b[i] = shared[read_B_offset + k_sub * 128 + i];
            }

#pragma unroll 8
            for (int m_sub = 0; m_sub < 8; m_sub++)
            {

#pragma unroll 8
                for (int n_sub = 0; n_sub < 8; n_sub++)
                {
                    result[n_sub * 8 + m_sub] += a[m_sub] * b[n_sub];
                }
            }
        }

        shared_offset ^= 64 * 8 * 2;
        read_A_offset ^= 64 * 8 * 2;
        read_B_offset ^= 64 * 8 * 2;
        track0 += ldx * 8;
        track1 += ldx * 8;
    }

#pragma unroll 8
    for (int m_sub = 0; m_sub < 8; m_sub++)
    {
        if (m_tile_offset * 64 + m_offset * 8 + m_sub >= M)
            continue;

#pragma unroll 8
        for (int n_sub = 0; n_sub < 8; n_sub++)
        {
            if (n_tile_offset * 64 + n_offset * 8 + n_sub >= N)
                continue;

            C[(m_tile_offset * 64 + m_offset * 8 + m_sub) * N + (n_tile_offset * 64 + n_offset * 8 + n_sub)] = result[n_sub * 8 + m_sub];
        }
    }
}
"""


def sgemm(op: Sgemm,
          constants_layout: MemoryLayout,
          variables_layout: MemoryLayout,
          metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    w = constants_layout[op.inputs["w"]]
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
        "sgemm_A_offset": x.offset,
        "sgemm_B_offset": w.offset,
        "sgemm_C_offset": y.offset,
        "sgemm_M": M,
        "sgemm_N": N,
        "sgemm_K": K
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("sgemm", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize((M + 64 - 1) // 64, (N + 64 - 1) // 64, 1),
        GPUSize(8, 8, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
