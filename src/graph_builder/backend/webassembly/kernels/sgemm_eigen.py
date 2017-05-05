from typing import List

from graph_builder.backend.webassembly.allocator import MemoryLayout
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels import util
from graph_builder.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webassembly.operators.sgemm import Sgemm


# sgemm using eigen

def generate_template(transpose_A, transpose_B):
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

    const int M = %%META_LOAD(sgemm_M, 1)%%;
    const int N = %%META_LOAD(sgemm_N, 1)%%;
    const int K = %%META_LOAD(sgemm_K, 1)%%;

    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%A_MAJOR%%> > a_mat(A, M, K);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%B_MAJOR%%> > b_mat(B, K, N);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(C, M, N);

    c_mat.noalias() = a_mat * b_mat;
}
""" \
        .replace("%%A_MAJOR%%", "RowMajor" if transpose_A else "ColMajor") \
        .replace("%%B_MAJOR%%", "RowMajor" if transpose_B else "ColMajor")


def sgemm_eigen(op: Sgemm,
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
    func_name = util.add_canonical_suffix("sgemm_eigen", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {
            func_name: source
        },
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
