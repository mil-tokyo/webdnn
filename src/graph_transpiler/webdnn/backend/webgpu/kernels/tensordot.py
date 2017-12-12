from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.util.misc import mul


def generate_template_64(M, N, K):
    return ("""
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_index_in_threadgroup]],
                          uint2 group_position[[threadgroup_position_in_grid]])
{
#define M_DIVIDABLE_BY_64 %%M_DIVIDABLE_BY_64%%
#define N_DIVIDABLE_BY_64 %%N_DIVIDABLE_BY_64%%
#define K_DIVIDABLE_BY_8 %%K_DIVIDABLE_BY_8%%

#define A_STRIDE_K M
#define A_STRIDE_M 1

#define B_STRIDE_K N
#define B_STRIDE_N 1

#if K_DIVIDABLE_BY_8 && M_DIVIDABLE_BY_64 && N_DIVIDABLE_BY_64 && OPTIMIZE
    const device float4 *load_target4 = (index & 32)
        ? (const device float4 *)(%%LOAD_BUFFER(sgemm_B)%%)
        : (const device float4 *)(%%LOAD_BUFFER(sgemm_A)%%);
#else
    const device float *load_target = (index & 32)
        ? (%%LOAD_BUFFER(sgemm_B)%%)
        : (%%LOAD_BUFFER(sgemm_A)%%);
#endif

    const int M = %%LOAD_BUFFER(sgemm_M)%%;
    const int N = %%LOAD_BUFFER(sgemm_N)%%;

    const int K = %%LOAD_BUFFER(sgemm_K)%%;

    threadgroup float4 shared4[32 * 8 * 2];

    const int stride_k = (index & 32) ? B_STRIDE_K : A_STRIDE_K;
    const int stride_mn = (index & 32) ? B_STRIDE_N : A_STRIDE_M;

    const int m_offset = index & 7;
    const int n_offset = index >> 3;

    const int mn_load_offset = ((index & 32) ? group_position.y : group_position.x) * 64 + (index & 15) * 4;
    const int k_load_offset = ((index & 16) ? 1 : 0);

    int track0 = mn_load_offset * stride_mn + (k_load_offset + 0) * stride_k;
    int track2 = track0 + 2 * stride_k;
    int track4 = track0 + 4 * stride_k;
    int track6 = track0 + 6 * stride_k;

#if !OPTIMIZE || !M_DIVIDABLE_BY_64 || !N_DIVIDABLE_BY_64
    const int max_MN = (index & 32) ? N : M;
#endif

    int shared_offset4 = ((index & 32) ? 16 : 0) + k_load_offset * 32 + (index & 15);
    int read_A_offset4 = m_offset * 2;
    int read_B_offset4 = n_offset * 2 + 16;

    float4 result[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    int k = 0;

    while (k < K)
    {
        {
#if OPTIMIZE && K_DIVIDABLE_BY_8
    #if OPTIMIZE && M_DIVIDABLE_BY_64 && N_DIVIDABLE_BY_64
        #if OPTIMIZE
            shared4[shared_offset4 + 32 * 0] = load_target4[track0 >> 2];
            shared4[shared_offset4 + 32 * 2] = load_target4[track2 >> 2];
            shared4[shared_offset4 + 32 * 4] = load_target4[track4 >> 2];
            shared4[shared_offset4 + 32 * 6] = load_target4[track6 >> 2];
        #else
            shared4[shared_offset4 + 32 * 0] = float4(
                load_target[track0 + stride_mn * 0],
                load_target[track0 + stride_mn * 1],
                load_target[track0 + stride_mn * 2],
                load_target[track0 + stride_mn * 3]
            );
            shared4[shared_offset4 + 32 * 2] = float4(
                load_target[track2 + stride_mn * 0],
                load_target[track2 + stride_mn * 1],
                load_target[track2 + stride_mn * 2],
                load_target[track2 + stride_mn * 3]
            );
            shared4[shared_offset4 + 32 * 4] = float4(
                load_target[track4 + stride_mn * 0],
                load_target[track4 + stride_mn * 1],
                load_target[track4 + stride_mn * 2],
                load_target[track4 + stride_mn * 3]
            );
            shared4[shared_offset4 + 32 * 6] = float4(
                load_target[track6 + stride_mn * 0],
                load_target[track6 + stride_mn * 1],
                load_target[track6 + stride_mn * 2],
                load_target[track6 + stride_mn * 3]
            );
        #endif
    #else
            shared4[shared_offset4 + 32 * 0] = float4(
                (mn_load_offset + 0 >= max_MN) ? 0 : load_target[track0 + stride_mn * 0],
                (mn_load_offset + 1 >= max_MN) ? 0 : load_target[track0 + stride_mn * 1],
                (mn_load_offset + 2 >= max_MN) ? 0 : load_target[track0 + stride_mn * 2],
                (mn_load_offset + 3 >= max_MN) ? 0 : load_target[track0 + stride_mn * 3]
            );
            shared4[shared_offset4 + 32 * 2] = float4(
                (mn_load_offset + 0 >= max_MN) ? 0 : load_target[track2 + stride_mn * 0],
                (mn_load_offset + 1 >= max_MN) ? 0 : load_target[track2 + stride_mn * 1],
                (mn_load_offset + 2 >= max_MN) ? 0 : load_target[track2 + stride_mn * 2],
                (mn_load_offset + 3 >= max_MN) ? 0 : load_target[track2 + stride_mn * 3]
            );
            shared4[shared_offset4 + 32 * 4] = float4(
                (mn_load_offset + 0 >= max_MN) ? 0 : load_target[track4 + stride_mn * 0],
                (mn_load_offset + 1 >= max_MN) ? 0 : load_target[track4 + stride_mn * 1],
                (mn_load_offset + 2 >= max_MN) ? 0 : load_target[track4 + stride_mn * 2],
                (mn_load_offset + 3 >= max_MN) ? 0 : load_target[track4 + stride_mn * 3]
            );
            shared4[shared_offset4 + 32 * 6] = float4(
                (mn_load_offset + 0 >= max_MN) ? 0 : load_target[track6 + stride_mn * 0],
                (mn_load_offset + 1 >= max_MN) ? 0 : load_target[track6 + stride_mn * 1],
                (mn_load_offset + 2 >= max_MN) ? 0 : load_target[track6 + stride_mn * 2],
                (mn_load_offset + 3 >= max_MN) ? 0 : load_target[track6 + stride_mn * 3]
            );
    #endif

            k += 8;
#else
    #if OPTIMIZE && M_DIVIDABLE_BY_64 && N_DIVIDABLE_BY_64
            shared4[shared_offset4 + 32 * 0] = float4(
                (k + k_load_offset >= K) ? 0 : load_target[track0 + stride_mn * 0],
                (k + k_load_offset >= K) ? 0 : load_target[track0 + stride_mn * 1],
                (k + k_load_offset >= K) ? 0 : load_target[track0 + stride_mn * 2],
                (k + k_load_offset >= K) ? 0 : load_target[track0 + stride_mn * 3]
            );
            k += 2;

            shared4[shared_offset4 + 32 * 2] = float4(
                (k + k_load_offset >= K) ? 0 : load_target[track2 + stride_mn * 0],
                (k + k_load_offset >= K) ? 0 : load_target[track2 + stride_mn * 1],
                (k + k_load_offset >= K) ? 0 : load_target[track2 + stride_mn * 2],
                (k + k_load_offset >= K) ? 0 : load_target[track2 + stride_mn * 3]
            );
            k += 2;

            shared4[shared_offset4 + 32 * 4] = float4(
                (k + k_load_offset >= K) ? 0 : load_target[track4 + stride_mn * 0],
                (k + k_load_offset >= K) ? 0 : load_target[track4 + stride_mn * 1],
                (k + k_load_offset >= K) ? 0 : load_target[track4 + stride_mn * 2],
                (k + k_load_offset >= K) ? 0 : load_target[track4 + stride_mn * 3]
            );
            k += 2;

            shared4[shared_offset4 + 32 * 6] = float4(
                (k + k_load_offset >= K) ? 0 : load_target[track6 + stride_mn * 0],
                (k + k_load_offset >= K) ? 0 : load_target[track6 + stride_mn * 1],
                (k + k_load_offset >= K) ? 0 : load_target[track6 + stride_mn * 2],
                (k + k_load_offset >= K) ? 0 : load_target[track6 + stride_mn * 3]
            );
            k += 2;
    #else
            shared4[shared_offset4 + 32 * 0] = float4(
                (k + k_load_offset >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track0 + stride_mn * 0],
                (k + k_load_offset >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track0 + stride_mn * 1],
                (k + k_load_offset >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track0 + stride_mn * 2],
                (k + k_load_offset >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track0 + stride_mn * 3]
            );
            k += 2;

            shared4[shared_offset4 + 32 * 2] = float4(
                (k + k_load_offset >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track2 + stride_mn * 0],
                (k + k_load_offset >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track2 + stride_mn * 1],
                (k + k_load_offset >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track2 + stride_mn * 2],
                (k + k_load_offset >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track2 + stride_mn * 3]
            );
            k += 2;

            shared4[shared_offset4 + 32 * 4] = float4(
                (k + k_load_offset >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track4 + stride_mn * 0],
                (k + k_load_offset >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track4 + stride_mn * 1],
                (k + k_load_offset >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track4 + stride_mn * 2],
                (k + k_load_offset >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track4 + stride_mn * 3]
            );
            k += 2;

            shared4[shared_offset4 + 32 * 6] = float4(
                (k + k_load_offset >= K || mn_load_offset + 0 >= max_MN) ? 0 : load_target[track6 + stride_mn * 0],
                (k + k_load_offset >= K || mn_load_offset + 1 >= max_MN) ? 0 : load_target[track6 + stride_mn * 1],
                (k + k_load_offset >= K || mn_load_offset + 2 >= max_MN) ? 0 : load_target[track6 + stride_mn * 2],
                (k + k_load_offset >= K || mn_load_offset + 3 >= max_MN) ? 0 : load_target[track6 + stride_mn * 3]
            );
            k += 2;
    #endif
#endif
        }

        threadgroup_barrier(mem_flags::mem_threadgroup);

        {
            for (int k_sub = 0; k_sub < 8; k_sub++)
            {
                float4 a00 = shared4[32 * k_sub + read_A_offset4 + 0];
                float4 a01 = shared4[32 * k_sub + read_A_offset4 + 1];
                float4 b00 = shared4[32 * k_sub + read_B_offset4 + 0];
                float4 b01 = shared4[32 * k_sub + read_B_offset4 + 1];

                result[4][0]  += b00[0] * a00[2];
                result[4][1]  += b00[1] * a00[2];
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

#if OPTIMIZE && N_DIVIDABLE_BY_64
        device float4 *C4 = (device float4 *)(%%LOAD_BUFFER(sgemm_C)%%);
        const int N4 = N >> 2;
        int m = group_position.x * 64 + m_offset * 8;
        for (int m_sub = 0; m_sub < 8; m_sub++)
        {

    #if !M_DIVIDABLE_BY_64
            if (m >= M) continue;
    #endif

            const int n = group_position.y * 16 + n_offset * 2;
            float4 result0 = result[m_sub * 2 + 0];
            float4 result1 = result[m_sub * 2 + 1];

            C4[m * N4 + n + 0] = result0;
            C4[m * N4 + n + 1] = result1;

            m++;
        }
#else
        device float *C = %%LOAD_BUFFER(sgemm_C)%%;
        int m = group_position.x * 64 + m_offset * 8;
        for (int m_sub = 0; m_sub < 8; m_sub++)
        {
            int n = group_position.y * 64 + n_offset * 8;

            for (int n_sub1 = 0; n_sub1 < 2; n_sub1++)
            {
                for (int n_sub2 = 0; n_sub2 < 4; n_sub2++)
                {

    #if OPTIMIZE && M_DIVIDABLE_BY_64
                    (         n < N) ? (C[m * N + n] = result[m_sub * 2 + n_sub1][n_sub2]) : 0;
    #else
                    (m < M && n < N) ? (C[m * N + n] = result[m_sub * 2 + n_sub1][n_sub2]) : 0;
    #endif
                    n++;
                }
            }

            m++;
        }
#endif

    }

#undef M_DIVIDABLE_BY_64
#undef N_DIVIDABLE_BY_64
#undef K_DIVIDABLE_BY_8
#undef A_STRIDE_K
#undef B_STRIDE_K
#undef A_STRIDE_M
#undef B_STRIDE_N
}
""") \
        .replace("%%M_DIVIDABLE_BY_64%%", "1" if M % 64 == 0 else "0") \
        .replace("%%N_DIVIDABLE_BY_64%%", "1" if N % 64 == 0 else "0") \
        .replace("%%K_DIVIDABLE_BY_8%%", "1" if K % 8 == 0 else "0")


@WebGPUDescriptorGenerator.register_handler(Tensordot)
def tensordot(op: Tensordot, memory_layout: MemoryLayout) -> List[Kernel]:
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]
    axes = op.axes

    # Reduced axes must be located on outside in input variables.
    assert A.order.axes[:len(axes[0])] == axes[0]
    assert B.order.axes[:len(axes[1])] == axes[1]

    # output variable's axes order must be as [*a_remained_axes, *b_remained_axes]
    assert C.order.axes[:A.ndim - len(axes[0])] == A.order.axes[len(axes[0]):]
    assert C.order.axes[-(B.ndim - len(axes[1])):] == B.order.axes[len(axes[1]):]
    assert C.ndim == A.ndim - len(axes[0]) + B.ndim - len(axes[1])

    K = mul(A.shape_dict[a] for a in axes[0])
    M = A.size // K
    N = B.size // K

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "sgemm_A": memory_layout[A],
        "sgemm_B": memory_layout[B],
        "sgemm_C": memory_layout[C],
        "sgemm_M": M,
        "sgemm_N": N,
        "sgemm_K": K
    })

    name_injector = KernelNameInjector(op)

    source = generate_template_64(M, N, K)
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize((M + 64 - 1) // 64, (N + 64 - 1) // 64, 1),
        GPUSize(64, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
