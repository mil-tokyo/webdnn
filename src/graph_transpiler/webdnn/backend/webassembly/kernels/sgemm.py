from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.operators.sgemm import Sgemm


def generate_template(transpose_A, transpose_B):
    return """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    float *A = %%LOAD_BUFFER(sgemm_A)%%;
    float *B = %%LOAD_BUFFER(sgemm_B)%%;
    float *C = %%LOAD_BUFFER(sgemm_C)%%;

    const int M = %%LOAD_BUFFER(sgemm_M)%%;
    const int N = %%LOAD_BUFFER(sgemm_N)%%;
    const int K = %%LOAD_BUFFER(sgemm_K)%%;

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

void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    float *A = %%LOAD_BUFFER(sgemm_A)%%;
    float *B = %%LOAD_BUFFER(sgemm_B)%%;
    float *C = %%LOAD_BUFFER(sgemm_C)%%;

    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%A_MAJOR%%> > a_mat(A, %%LOAD_BUFFER(sgemm_M)%%, %%LOAD_BUFFER(sgemm_K)%%);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%B_MAJOR%%> > b_mat(B, %%LOAD_BUFFER(sgemm_K)%%, %%LOAD_BUFFER(sgemm_N)%%);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(C, %%LOAD_BUFFER(sgemm_M)%%, %%LOAD_BUFFER(sgemm_N)%%);

    c_mat.noalias() = a_mat * b_mat;
}
""" \
        .replace("%%A_MAJOR%%", "RowMajor" if transpose_A else "ColMajor") \
        .replace("%%B_MAJOR%%", "RowMajor" if transpose_B else "ColMajor")


@WebassemblyDescriptorGenerator.register_handler(Sgemm)
def sgemm(op: Sgemm, memory_layout: MemoryLayout) -> List[Kernel]:
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "sgemm_A": memory_layout[A],
        "sgemm_B": memory_layout[B],
        "sgemm_C": memory_layout[C],
        "sgemm_M": op.M,
        "sgemm_N": op.N,
        "sgemm_K": op.K
    })

    if op.parameters["eigen"]:
        source = generate_template_eigen(op.transpose_A, op.transpose_B, op.M, op.N, op.K)
        buffer_injector.register({
            "sgemm_A": memory_layout[A],
            "sgemm_B": memory_layout[B],
            "sgemm_C": memory_layout[C]
        })

    else:
        source = generate_template(op.transpose_A, op.transpose_B)
        buffer_injector.register({
            "sgemm_A": memory_layout[A],
            "sgemm_B": memory_layout[B],
            "sgemm_C": memory_layout[C],
            "sgemm_M": op.M,
            "sgemm_N": op.N,
            "sgemm_K": op.K
        })

    name_injector = KernelNameInjector(op)

    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
