#include <metal_stdlib>
using namespace metal;

kernel void sgemm64(const device int *MNK[[buffer(0)]],
                    const device float *ab[[buffer(1)]],
                    const device float *A[[buffer(2)]],
                    const device float *B[[buffer(3)]],
                    device float *C[[buffer(4)]],
                    uint index[[thread_index_in_threadgroup]],
                    uint2 group_position[[threadgroup_position_in_grid]])
{
    const int M = MNK[0];
    const int N = MNK[1];
    const int K = MNK[2];

    const float alpha = ab[0];
    const float beta = ab[1];

    const int m_tile_offset = group_position.x;
    const int n_tile_offset = group_position.y;
    const int m_offset = index % 8;
    const int n_offset = index / 8;

    threadgroup float shared[64 * 8 * 2 * 2];

    const device float *load_target = (index >= 32) ? B : A;
    const int ldx = (index >= 32) ? 1 : M;
    int track0 = (index >= 32) ? ((n_tile_offset * 64 + index - 32) * K) : (m_tile_offset * 64 + index);
    int track1 = (index >= 32) ? (track0 + 32 * K) : (track0 + 32);
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
            shared[shared_offset + k_sub * 128 + 32 * 0] = load_target[track0 + k_sub * ldx];
            shared[shared_offset + k_sub * 128 + 32 * 1] = load_target[track1 + k_sub * ldx];
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

    for (int m_sub = 0; m_sub < 8; m_sub++)
    {

#pragma unroll 8
        for (int n_sub = 0; n_sub < 8; n_sub++)
        {
            C[(n_tile_offset * 64 + n_offset * 8 + n_sub) * M + m_tile_offset * 64 + m_offset * 8 + m_sub] =
                alpha * result[n_sub * 8 + m_sub] +
                beta * C[(n_tile_offset * 64 + n_offset * 8 + n_sub) * M + m_tile_offset * 64 + m_offset * 8 + m_sub];
        }
    }
}

kernel void sgemm_naive(const device int *MNK[[buffer(0)]],
                        const device float *ab[[buffer(1)]],
                        const device float *A[[buffer(2)]],
                        const device float *B[[buffer(3)]],
                        device float *C[[buffer(4)]],
                        uint gid[[thread_position_in_grid]])
{
    const int M = MNK[0];
    const int N = MNK[1];
    const int K = MNK[2];

    const float alpha = ab[0];
    const float beta = ab[1];

    if (gid >= M * N)
        return;

    const int m = gid % M;
    const int n = gid / M;

    float r = 0;

    for (int k = 0; k < K; k++)
        r += A[k * M + m] * B[n * K + k];

    C[n * M + m] = alpha * r + beta * C[n * M + m];
}