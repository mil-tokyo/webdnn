from typing import List

from graph_transpiler.backend.webassembly.inline_injector import InlineInjector
from graph_transpiler.backend.webgpu.allocator import MemoryLayout
from graph_transpiler.backend.webgpu.kernel import Kernel, GPUSize
from graph_transpiler.backend.webgpu.kernels import util
from graph_transpiler.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_transpiler.backend.webgpu.operators.sgemm import Sgemm

prototype_sgemm_core = """
void %%CORE_NAME%%(const device float*, const device float*, device float*, 
                   const int, const int, const int,
                   const int, const int,
                   threadgroup float4*, 
                   ushort, ushort2);
"""


def generate_template(transpose_A, transpose_B, with_bias=False):
    return """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          ushort index[[thread_index_in_threadgroup]],
                          ushort2 group_position[[threadgroup_position_in_grid]])
{
    device float *C = data_buffer + %%META_LOAD(sgemm_C_offset)%%;

    const device float *load_target = (index & 32) 
        ? (weight_buffer + %%META_LOAD(sgemm_B_offset)%%) 
        : (data_buffer + %%META_LOAD(sgemm_A_offset)%%);

    const int M = %%META_LOAD(sgemm_M)%%;
    const int N = %%META_LOAD(sgemm_N)%%;
    const int K = %%META_LOAD(sgemm_K)%%;

    const device float *bias = %%BIAS%%;

    threadgroup float4 shared4[32 * 8 * 2];

    const int stride_k = (index & 32) ? %%B_STRIDE_K%% : %%A_STRIDE_K%%;
    const int stride_mn = (index & 32) ? %%B_STRIDE_MN%% : %%A_STRIDE_MN%%;

    %%CORE_NAME%%(load_target, bias, C, M, N, K, stride_k, stride_mn, shared4, index, group_position);
}
""" \
        .replace("%%A_STRIDE_K%%", "1" if transpose_A else "M") \
        .replace("%%B_STRIDE_K%%", "N" if transpose_B else "1") \
        .replace("%%A_STRIDE_MN%%", "K" if transpose_A else "1") \
        .replace("%%B_STRIDE_MN%%", "1" if transpose_B else "K") \
        .replace("%%BIAS%%", "weight_buffer + %%META_LOAD(sgemm_b_offset)%%" if with_bias else "nullptr")


def generate_sgemm_core(with_bias=False):
    return """
void %%CORE_NAME%%(const device float *load_target,
                   const device float *bias,
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
    int k = 0;

    while (k < K)
    {
        {
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
""" + ("""
        float b[8];
    #pragma unroll 8
        for (int n_sub = 0; n_sub < 8; n_sub++)
        {

            b[n_sub] = (group_position.y * 64 + n_offset * 8 + n_sub < N)
                ? bias[group_position.y * 64 + n_offset * 8 + n_sub]
                : 0;
        }
""" if with_bias else """
""") + """
#pragma unroll 8
        for (int m_sub = 0; m_sub < 8; m_sub++)
        {
#pragma unroll 2
            for (int n_sub1 = 0; n_sub1 < 2; n_sub1++)
            {
#pragma unroll 4
                for (int n_sub2 = 0; n_sub2 < 4; n_sub2++)
                {
                    const int m = group_position.x * 64 + m_offset * 8 + m_sub;
                    const int n = group_position.y * 64 + n_offset * 8 + n_sub1 * 4 + n_sub2;
""" + ("""
                    (m < M && n < N) ? (C[m * N + n] = %%INLINE(b[n_sub1*4+n_sub2] + result[m_sub * 2 + n_sub1][n_sub2])%%) : 0;
""" if with_bias else """
                    (m < M && n < N) ? (C[m * N + n] = %%INLINE(result[m_sub * 2 + n_sub1][n_sub2])%%) : 0;
""") + """
                }
            }
        }
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

    with_bias = "b" in op.inputs

    if with_bias:
        metabuffer_injector.register({
            "sgemm_b_offset": constants_layout[op.inputs["b"]].offset
        })

    inline_injector = InlineInjector()
    if "inline_elementwise" in op.parameters:
        inline_injector.delegate = op.parameters["inline_elementwise"]

    # transpose_X assumes fortran-order data. True means X is C-order, False means Fortran-order.
    # In default convolution, transpose_A == transpose_B == True.
    # The order of output matrix C is C-order.
    core_source = inline_injector.inject(generate_sgemm_core(with_bias=with_bias))
    core_name = util.add_canonical_suffix("sgemm_core", core_source)
    core_source = core_source.replace("%%CORE_NAME%%", core_name)
    prototype_source = prototype_sgemm_core.replace("%%CORE_NAME%%", core_name)

    func_source = generate_template(op.transpose_A, op.transpose_B, with_bias=with_bias)
    func_source = metabuffer_injector.inject(func_source)
    func_source = func_source.replace("%%CORE_NAME%%", core_name)
    func_name = util.add_canonical_suffix("sgemm", func_source)
    func_source = func_source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {
            func_name: func_source,
            core_name: core_source
        },
        func_name,
        GPUSize((op.M + 64 - 1) // 64, (op.N + 64 - 1) // 64, 1),
        GPUSize(64, 1, 1),
        metabuffer_injector.generate_buffer(),
        {
            core_name: prototype_source
        }
    )

    return [kernel]
