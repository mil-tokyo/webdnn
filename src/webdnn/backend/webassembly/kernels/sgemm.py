from typing import List

from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.kernels import util
from webdnn.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from webdnn.backend.webassembly.operators.sgemm import Sgemm
from webdnn.backend.webgpu.allocator import MemoryLayout


def generate_template(transpose_A, transpose_B):
    return """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    float *A = data_buffer + %%META_LOAD(sgemm_A_offset, 1)%%;
    float *B = weight_buffer + %%META_LOAD(sgemm_B_offset, 1)%%;
    float *C = data_buffer + %%META_LOAD(sgemm_C_offset, 1)%%;

    const int M = %%META_LOAD(sgemm_M, 1)%%;
    const int N = %%META_LOAD(sgemm_N, 1)%%;
    const int K = %%META_LOAD(sgemm_K, 1)%%;

    const int a_stride_k = %%A_STRIDE_K%%;
    const int a_stride_mn = %%A_STRIDE_MN%%;
    const int b_stride_k = %%B_STRIDE_K%%;
    const int b_stride_mn = %%B_STRIDE_MN%%;

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < N; j++) {
            float sum = 0.0;
            for (int s = 0; s < K; s++) {
                sum += A[i * a_stride_mn + s * a_stride_k] * B[j * b_stride_mn + s * b_stride_k];
            }
            C[i * N + j * 1] = sum;
        }
    }
}
""" \
        .replace("%%A_STRIDE_K%%", "1" if transpose_A else "M") \
        .replace("%%B_STRIDE_K%%", "N" if transpose_B else "1") \
        .replace("%%A_STRIDE_MN%%", "K" if transpose_A else "1") \
        .replace("%%B_STRIDE_MN%%", "1" if transpose_B else "K")


# sgemm using eigen

def generate_template_eigen(transpose_A, transpose_B, M, N, K):
    return """
#ifndef INCLUDE_EIGEN
#define INCLUDE_EIGEN
#include <Eigen/Dense>
#endif

void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    float *A = data_buffer + %%META_LOAD(sgemm_A_offset, 1)%%;
    float *B = weight_buffer + %%META_LOAD(sgemm_B_offset, 1)%%;
    float *C = data_buffer + %%META_LOAD(sgemm_C_offset, 1)%%;

    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%A_MAJOR%%> > a_mat(A, %%M%%, %%K%%);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%B_MAJOR%%> > b_mat(B, %%K%%, %%N%%);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(C, %%M%%, %%N%%);
    //Eigen::Map<Eigen::Matrix<float, %%M%%, %%K%%, Eigen::%%A_MAJOR%%> > a_mat(A, %%M%%, %%K%%);
    //Eigen::Map<Eigen::Matrix<float, %%K%%, %%N%%, Eigen::%%B_MAJOR%%> > b_mat(B, %%K%%, %%N%%);
    //Eigen::Map<Eigen::Matrix<float, %%M%%, %%N%%, Eigen::RowMajor> > c_mat(C, %%M%%, %%N%%);

    c_mat.noalias() = a_mat * b_mat;
}
""" \
        .replace("%%A_MAJOR%%", "RowMajor" if transpose_A else "ColMajor") \
        .replace("%%B_MAJOR%%", "RowMajor" if transpose_B else "ColMajor") \
        .replace("%%M%%", str(M)) \
        .replace("%%N%%", str(N)) \
        .replace("%%K%%", str(K))


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

    if op.parameters["eigen"]:
        source = generate_template_eigen(op.transpose_A, op.transpose_B, op.M, op.N, op.K)

        metabuffer_injector.register({
            "sgemm_A_offset": A.offset,
            "sgemm_B_offset": B.offset,
            "sgemm_C_offset": C.offset
        })
    else:
        source = generate_template(op.transpose_A, op.transpose_B)

        metabuffer_injector.register({
            "sgemm_A_offset": A.offset,
            "sgemm_B_offset": B.offset,
            "sgemm_C_offset": C.offset,
            "sgemm_M": op.M,
            "sgemm_N": op.N,
            "sgemm_K": op.K
        })
    source = metabuffer_injector.inject(source)
    func_name = util.add_canonical_suffix("sgemm", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {
            func_name: source
        },
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
