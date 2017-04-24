from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.sgemm import Sgemm
from graph_builder.graph.variables.attributes.order import OrderCNHW

template_cnhw = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_index_in_threadgroup]],
                          uint2 group_position[[threadgroup_position_in_grid]])
{
#define TILESIZE_K 8
#define TILESIZE_M 64
#define TILESIZE_N 64
#define CELLSIZE_M 8
#define CELLSIZE_N 8
#define NUM_CELL_M (TILESIZE_M / CELLSIZE_M)
#define NUM_CELL_N (TILESIZE_N / CELLSIZE_N)
#define NUM_REPEAT_IN_TILE 2

    const device float *A = data_buffer + %%META_LOAD(sgemm_A_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(sgemm_B_offset)%%;
    device float *C = data_buffer + %%META_LOAD(sgemm_C_offset)%%;

    const int M = %%META_LOAD(sgemm_M)%%;
    const int N = %%META_LOAD(sgemm_N)%%;
    const int K = %%META_LOAD(sgemm_K)%%;

    const int m_tile_offset = group_position.x;
    const int n_tile_offset = group_position.y;
    const int m_offset = index % NUM_CELL_M;
    const int n_offset = index / NUM_CELL_M;

    threadgroup float shared[(TILESIZE_M + TILESIZE_N) * TILESIZE_K * 2];

    const device float *load_target = (index >= 32) ? B : A;
    const int ld1 = (index >= 32) ? N : M;
    const int ld2 = TILESIZE_N / NUM_REPEAT_IN_TILE;
    int track = (index >= 32) ? (n_tile_offset * TILESIZE_N + index - 32) : (m_tile_offset * TILESIZE_M + index);
    const int track_offset = track;
    const int track_max = (index >= 32) ? N : M;
    int shared_offset = (index >= 32) ? (index - 32 + TILESIZE_M) : index;
    int read_A_offset = m_offset * CELLSIZE_M;
    int read_B_offset = n_offset * CELLSIZE_N + TILESIZE_M;

    float result[CELLSIZE_M * CELLSIZE_N];

#pragma unroll CELLSIZE_M * CELLSIZE_N
    for (int i = 0; i < CELLSIZE_M * CELLSIZE_N; i++)
        result[i] = 0;

    for (int k = 0; k < K; k += TILESIZE_K)
    {
//Load data
#pragma unroll TILESIZE_K
        for (int i = 0; i < TILESIZE_K; i++)
        {
#pragma unroll NUM_REPEAT_IN_TILE
            for (int j = 0; j < NUM_REPEAT_IN_TILE; j++) {
                shared[shared_offset + (TILESIZE_N + TILESIZE_M) * i + 32 * j] = (k + i >= K || track_offset + ld2 * j >= track_max) 
                ? 0
                : load_target[ld1 * i + track + ld2 * j];
            }
        }

        //sync all threads in threadgroup
        threadgroup_barrier(mem_flags::mem_none);

#pragma unroll TILESIZE_K
        for (int i = 0; i < TILESIZE_K; i++)
        {
            float a[CELLSIZE_M];
            float b[CELLSIZE_N];

#pragma unroll CELLSIZE_M
            for (int j = 0; j < CELLSIZE_M; j++)
            {
                a[j] = shared[(TILESIZE_M + TILESIZE_N) * i + read_A_offset + j];
            }

#pragma unroll CELLSIZE_N
            for (int j = 0; j < CELLSIZE_N; j++)
            {
                b[j] = shared[(TILESIZE_M + TILESIZE_N) * i + read_B_offset + j];
            }

#pragma unroll CELLSIZE_M
            for (int m_sub = 0; m_sub < CELLSIZE_M; m_sub++)
            {

#pragma unroll CELLSIZE_N
                for (int n_sub = 0; n_sub < CELLSIZE_N; n_sub++)
                {
                    result[n_sub * CELLSIZE_M + m_sub] += a[m_sub] * b[n_sub];
                }
            }
        }

        shared_offset ^= (TILESIZE_M + TILESIZE_N) * TILESIZE_K;
        read_A_offset ^= (TILESIZE_M + TILESIZE_N) * TILESIZE_K;
        read_B_offset ^= (TILESIZE_M + TILESIZE_N) * TILESIZE_K;
        track += ld1 * TILESIZE_K;
    }

#pragma unroll CELLSIZE_N
    for (int n_sub = 0; n_sub < CELLSIZE_N; n_sub++)
    {
        if (n_tile_offset * TILESIZE_N + n_offset * CELLSIZE_N + n_sub >= N)
            continue;

    #pragma unroll CELLSIZE_M
        for (int m_sub = 0; m_sub < CELLSIZE_M; m_sub++)
        {
            if (m_tile_offset * TILESIZE_M + m_offset * CELLSIZE_M + m_sub >= M)
                continue;

            C[(m_tile_offset * TILESIZE_M + m_offset * CELLSIZE_M + m_sub) * N + (n_tile_offset * TILESIZE_N + n_offset * CELLSIZE_N + n_sub)]
                = result[n_sub * CELLSIZE_M + m_sub];
        }
    }

#undef TILESIZE_K
#undef TILESIZE_M
#undef TILESIZE_N
}
"""

template_nhwc = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_index_in_threadgroup]],
                          uint2 group_position[[threadgroup_position_in_grid]])
{
#define TILESIZE_K 8
#define TILESIZE_M 64
#define TILESIZE_N 64
#define CELLSIZE_M 8
#define CELLSIZE_N 8
#define NUM_CELL_M (TILESIZE_M / CELLSIZE_M)
#define NUM_CELL_N (TILESIZE_N / CELLSIZE_N)
#define NUM_REPEAT_IN_TILE 2

    const device float *A = data_buffer + %%META_LOAD(sgemm_A_offset)%%;
    const device float *B = weight_buffer + %%META_LOAD(sgemm_B_offset)%%;
    device float *C = data_buffer + %%META_LOAD(sgemm_C_offset)%%;

    const int M = %%META_LOAD(sgemm_M)%%;
    const int N = %%META_LOAD(sgemm_N)%%;
    const int K = %%META_LOAD(sgemm_K)%%;

    const int m_tile_offset = group_position.x;
    const int n_tile_offset = group_position.y;
    const int m_offset = index % NUM_CELL_M;
    const int n_offset = index / NUM_CELL_M;

    threadgroup float shared[(TILESIZE_M + TILESIZE_N) * TILESIZE_K * 2];

    const device float *load_target = (index >= 32) ? B : A;
    const int ld1 = (index >= 32) ? N : 1;
    const int ld2 = (index >= 32) ? (TILESIZE_N / NUM_REPEAT_IN_TILE) : (TILESIZE_M / NUM_REPEAT_IN_TILE * K);
    int track = (index >= 32) ? (n_tile_offset * TILESIZE_N + index - 32) : ((m_tile_offset * TILESIZE_M + index) * K);
    const int track_offset = track;
    const int track_max = (index >= 32) ? N : (M * K);
    int shared_offset = (index >= 32) ? (index - 32 + TILESIZE_M) : index;
    int read_A_offset = m_offset * CELLSIZE_M;
    int read_B_offset = n_offset * CELLSIZE_N + TILESIZE_M;

    float result[CELLSIZE_M * CELLSIZE_N];

#pragma unroll CELLSIZE_M * CELLSIZE_N
    for (int i = 0; i < CELLSIZE_M * CELLSIZE_N; i++)
        result[i] = 0;

    for (int k = 0; k < K; k += TILESIZE_K)
    {
//Load data
#pragma unroll TILESIZE_K
        for (int i = 0; i < TILESIZE_K; i++)
        {
#pragma unroll NUM_REPEAT_IN_TILE
            for (int j = 0; j < NUM_REPEAT_IN_TILE; j++) {
                shared[shared_offset + (TILESIZE_N + TILESIZE_M) * i + 32 * j] = (k + i >= K || track_offset + ld2 * j >= track_max) 
                ? 0
                : load_target[ld1 * i + track + ld2 * j];
            }
        }

        //sync all threads in threadgroup
        threadgroup_barrier(mem_flags::mem_none);

#pragma unroll TILESIZE_K
        for (int i = 0; i < TILESIZE_K; i++)
        {
            float a[CELLSIZE_M];
            float b[CELLSIZE_N];

#pragma unroll CELLSIZE_M
            for (int j = 0; j < CELLSIZE_M; j++)
            {
                a[j] = shared[(TILESIZE_M + TILESIZE_N) * i + read_A_offset + j];
            }

#pragma unroll CELLSIZE_N
            for (int j = 0; j < CELLSIZE_N; j++)
            {
                b[j] = shared[(TILESIZE_M + TILESIZE_N) * i + read_B_offset + j];
            }

#pragma unroll CELLSIZE_M
            for (int m_sub = 0; m_sub < CELLSIZE_M; m_sub++)
            {

#pragma unroll CELLSIZE_N
                for (int n_sub = 0; n_sub < CELLSIZE_N; n_sub++)
                {
                    result[n_sub * CELLSIZE_M + m_sub] += a[m_sub] * b[n_sub];
                }
            }
        }

        shared_offset ^= (TILESIZE_M + TILESIZE_N) * TILESIZE_K;
        read_A_offset ^= (TILESIZE_M + TILESIZE_N) * TILESIZE_K;
        read_B_offset ^= (TILESIZE_M + TILESIZE_N) * TILESIZE_K;
        track += ld1 * TILESIZE_K;
    }

#pragma unroll CELLSIZE_N
    for (int n_sub = 0; n_sub < CELLSIZE_N; n_sub++)
    {
        if (n_tile_offset * TILESIZE_N + n_offset * CELLSIZE_N + n_sub >= N)
            continue;

#pragma unroll CELLSIZE_M
        for (int m_sub = 0; m_sub < CELLSIZE_M; m_sub++)
        {
            if (m_tile_offset * TILESIZE_M + m_offset * CELLSIZE_M + m_sub >= M)
                continue;

            C[(m_tile_offset * TILESIZE_M + m_offset * CELLSIZE_M + m_sub) * N + (n_tile_offset * TILESIZE_N + n_offset * CELLSIZE_N + n_sub)]
                = result[n_sub * CELLSIZE_M + m_sub];
        }
    }

#undef TILESIZE_K
#undef TILESIZE_M
#undef TILESIZE_N
}
"""


def sgemm(op: Sgemm,
          constants_layout: MemoryLayout,
          variables_layout: MemoryLayout,
          metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    A = variables_layout[op.inputs["A"]] if op.inputs["A"] in variables_layout else constants_layout[op.inputs["A"]]
    B = variables_layout[op.inputs["B"]] if op.inputs["B"] in variables_layout else constants_layout[op.inputs["B"]]
    C = variables_layout[op.outputs["C"]]

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "sgemm_A_offset": A.offset,
        "sgemm_B_offset": B.offset,
        "sgemm_C_offset": C.offset,
        "sgemm_M": op.M,
        "sgemm_N": op.N,
        "sgemm_K": op.K
    })

    source = template_cnhw if A.variable.axis_order == OrderCNHW else template_nhwc
    source = metabuffer_injector.inject(source)
    func_name = util.add_canonical_suffix("sgemm", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize((op.M + 64 - 1) // 64, (op.N + 64 - 1) // 64, 1),
        GPUSize(64, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
