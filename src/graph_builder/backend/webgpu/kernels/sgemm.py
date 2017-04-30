from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.sgemm import Sgemm

prototype_sgemm_core = """
void sgemm_core(const device float*, device float*, 
                const int, const int, const int,
                const int, const int,
                threadgroup float4*, 
                ushort, ushort2);
"""


def generate_template(transpose_A, transpose_B):
    return """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          ushort index[[thread_index_in_threadgroup]],
                          ushort2 group_position[[threadgroup_position_in_grid]])
{
    device float *C = data_buffer + %%META_LOAD(sgemm_C_offset, 1)%%;

    const device float *load_target = (index & 32) 
        ? (weight_buffer + %%META_LOAD(sgemm_B_offset, 1)%%) 
        : (data_buffer + %%META_LOAD(sgemm_A_offset, 1)%%);

    const int M = %%META_LOAD(sgemm_M, 1)%%;
    const int N = %%META_LOAD(sgemm_N, 1)%%;
    const int K = %%META_LOAD(sgemm_K, 1)%%;

    threadgroup float4 shared4[32 * 8 * 2];

    const int stride_k = (index & 32) ? %%B_STRIDE_K%% : %%A_STRIDE_K%%;
    const int stride_mn = (index & 32) ? %%B_STRIDE_MN%% : %%A_STRIDE_MN%%;

    sgemm_core(load_target, C, M, N, K, stride_k, stride_mn, shared4, index, group_position);
}
""" \
        .replace("%%A_STRIDE_K%%", "1" if transpose_A else "M") \
        .replace("%%B_STRIDE_K%%", "N" if transpose_B else "1") \
        .replace("%%A_STRIDE_MN%%", "K" if transpose_A else "1") \
        .replace("%%B_STRIDE_MN%%", "1" if transpose_B else "K")


template_sgemm_core = """
void sgemm_core(const device float *load_target,
                device float *C,
                const int M,
                const int N,
                const int K,
                const int stride_k,
                const int stride_mn,
                threadgroup float4 *shared4,
                ushort index,
                ushort2 group_position) 
{
    const int m_offset = index & 7;
    const int n_offset = index >> 3;

    const int mn_load_offset = ((index & 32) ? group_position.y : group_position.x) * 64 + (index & 15) * 4;
    const int k_load_offset = ((index & 16) ? 1 : 0);

    int track0 = mn_load_offset * stride_mn + (k_load_offset + 0) * stride_k;
    int track2 = track0 + 2 * stride_k;
    int track4 = track0 + 4 * stride_k;
    int track6 = track0 + 6 * stride_k;

    const int max_MN = (index & 32) ? N : M;

    int shared_offset4 = ((index & 32) ? 16 : 0) + k_load_offset * 32 + (index & 15);
    int read_A_offset4 = m_offset * 2;
    int read_B_offset4 = n_offset * 2 + 16;

    float4 result[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    int k = k_load_offset;

    while (k < K)
    {
        {
            shared4[shared_offset4 + 32 * 0] = float4(
                (k >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track0 + stride_mn * 0],
                (k >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track0 + stride_mn * 1],
                (k >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track0 + stride_mn * 2],
                (k >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track0 + stride_mn * 3]
            ); 
            k += 2;

            shared4[shared_offset4 + 32 * 2] = float4(
                (k >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track2 + stride_mn * 0],
                (k >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track2 + stride_mn * 1],
                (k >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track2 + stride_mn * 2],
                (k >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track2 + stride_mn * 3]
            ); 
            k += 2;

            shared4[shared_offset4 + 32 * 4] = float4(
                (k >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track4 + stride_mn * 0],
                (k >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track4 + stride_mn * 1],
                (k >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track4 + stride_mn * 2],
                (k >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track4 + stride_mn * 3]
            ); 
            k += 2;

            shared4[shared_offset4 + 32 * 6] = float4(
                (k >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track6 + stride_mn * 0],
                (k >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track6 + stride_mn * 1],
                (k >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track6 + stride_mn * 2],
                (k >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track6 + stride_mn * 3]
            ); 
            k += 2;
        }

        threadgroup_barrier(mem_flags::mem_threadgroup);

        {
#pragma unroll 8
            for (int k_sub = 0; k_sub < 8; k_sub++)
            {
                float4 a00 = shared4[32 * k_sub + read_A_offset4 + 0];
                float4 a01 = shared4[32 * k_sub + read_A_offset4 + 1];
                float4 b00 = shared4[32 * k_sub + read_B_offset4 + 0];
                float4 b01 = shared4[32 * k_sub + read_B_offset4 + 1];

                result[4][0]  = fma(b00[0], a00[2], result[4][0]);
                result[4][1]  = fma(b00[1], a00[2], result[4][1]);
                result[0][1]  += b00[1] * a00[0];
                result[0][0]  += b00[0] * a00[0];
                result[6][0]  += b00[0] * a00[3];
                result[6][1]  += b00[1] * a00[3];
                result[2][1]  += b00[1] * a00[1];
                result[2][0]  += b00[0] * a00[1];
                result[12][0] += b00[0] * a01[2];
                result[12][1] += b00[1] * a01[2];
                result[8][1]  += b00[1] * a01[0];
                result[8][0]  += b00[0] * a01[0];
                result[14][0] += b00[0] * a01[3];
                result[14][1] += b00[1] * a01[3];
                result[10][1] += b00[1] * a01[1];
                result[10][0] += b00[0] * a01[1];

                result[14][2] += b00[2] * a01[3];
                result[14][3] += b00[3] * a01[3];
                result[10][3] += b00[3] * a01[1];
                result[10][2] += b00[2] * a01[1];
                result[12][2] += b00[2] * a01[2];
                result[12][3] += b00[3] * a01[2];
                result[8][3]  += b00[3] * a01[0];
                result[8][2]  += b00[2] * a01[0];
                result[6][2]  += b00[2] * a00[3];
                result[6][3]  += b00[3] * a00[3];
                result[2][3]  += b00[3] * a00[1];
                result[2][2]  += b00[2] * a00[1];
                result[4][2]  += b00[2] * a00[2];
                result[4][3]  += b00[3] * a00[2];
                result[0][3]  += b00[3] * a00[0];
                result[0][2]  += b00[2] * a00[0];

                result[5][0]  += b01[0] * a00[2];
                result[5][1]  += b01[1] * a00[2];
                result[1][1]  += b01[1] * a00[0];
                result[1][0]  += b01[0] * a00[0];
                result[7][0]  += b01[0] * a00[3];
                result[7][1]  += b01[1] * a00[3];
                result[3][1]  += b01[1] * a00[1];
                result[3][0]  += b01[0] * a00[1];
                result[13][0] += b01[0] * a01[2];
                result[13][1] += b01[1] * a01[2];
                result[9][1]  += b01[1] * a01[0];
                result[9][0]  += b01[0] * a01[0];
                result[15][0] += b01[0] * a01[3];
                result[15][1] += b01[1] * a01[3];
                result[11][1] += b01[1] * a01[1];
                result[11][0] += b01[0] * a01[1];

                result[15][2] += b01[2] * a01[3];
                result[15][3] += b01[3] * a01[3];
                result[11][3] += b01[3] * a01[1];
                result[11][2] += b01[2] * a01[1];
                result[13][2] += b01[2] * a01[2];
                result[13][3] += b01[3] * a01[2];
                result[9][3]  += b01[3] * a01[0];
                result[9][2]  += b01[2] * a01[0];
                result[7][2]  += b01[2] * a00[3];
                result[7][3]  += b01[3] * a00[3];
                result[3][3]  += b01[3] * a00[1];
                result[3][2]  += b01[2] * a00[1];
                result[5][2]  += b01[2] * a00[2];
                result[5][3]  += b01[3] * a00[2];
                result[1][3]  += b01[3] * a00[0];
                result[1][2]  += b01[2] * a00[0];
            }
        }

        shared_offset4 ^= 32 * 8;
        read_A_offset4 ^= 32 * 8;
        read_B_offset4 ^= 32 * 8;
        track0 += stride_k * 8;
        track2 += stride_k * 8;
        track4 += stride_k * 8;
        track6 += stride_k * 8;
    }

    {
        int m = group_position.x * 64 + m_offset * 8;
        int n = group_position.y * 64 + n_offset * 8;

        (m + 0 < M) ? (*((device float4 *)(&C[(m + 0) * N + n + 0])) = result[0]) : 0;
        (m + 0 < M) ? (*((device float4 *)(&C[(m + 0) * N + n + 4])) = result[1]) : 0;
        (m + 1 < M) ? (*((device float4 *)(&C[(m + 1) * N + n + 0])) = result[2]) : 0;
        (m + 1 < M) ? (*((device float4 *)(&C[(m + 1) * N + n + 4])) = result[3]) : 0;
        (m + 2 < M) ? (*((device float4 *)(&C[(m + 2) * N + n + 0])) = result[4]) : 0;
        (m + 2 < M) ? (*((device float4 *)(&C[(m + 2) * N + n + 4])) = result[5]) : 0;
        (m + 3 < M) ? (*((device float4 *)(&C[(m + 3) * N + n + 0])) = result[6]) : 0;
        (m + 3 < M) ? (*((device float4 *)(&C[(m + 3) * N + n + 4])) = result[7]) : 0;
        (m + 4 < M) ? (*((device float4 *)(&C[(m + 4) * N + n + 0])) = result[8]) : 0;
        (m + 4 < M) ? (*((device float4 *)(&C[(m + 4) * N + n + 4])) = result[9]) : 0;
        (m + 5 < M) ? (*((device float4 *)(&C[(m + 5) * N + n + 0])) = result[10]) : 0;
        (m + 5 < M) ? (*((device float4 *)(&C[(m + 5) * N + n + 4])) = result[11]) : 0;
        (m + 6 < M) ? (*((device float4 *)(&C[(m + 6) * N + n + 0])) = result[12]) : 0;
        (m + 6 < M) ? (*((device float4 *)(&C[(m + 6) * N + n + 4])) = result[13]) : 0;
        (m + 7 < M) ? (*((device float4 *)(&C[(m + 7) * N + n + 0])) = result[14]) : 0;
        (m + 7 < M) ? (*((device float4 *)(&C[(m + 7) * N + n + 4])) = result[15]) : 0;
    }
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

    source = generate_template(op.transpose_A, op.transpose_B)
    source = metabuffer_injector.inject(source)
    func_name = util.add_canonical_suffix("sgemm", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {
            func_name: source,
            "sgemm_core": template_sgemm_core
        },
        func_name,
        GPUSize((op.M + 64 - 1) // 64, (op.N + 64 - 1) // 64, 1),
        GPUSize(64, 1, 1),
        metabuffer_injector.generate_buffer(),
        {
            "sgemm_core": prototype_sgemm_core
        }
    )

    return [kernel]
