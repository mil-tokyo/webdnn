from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.optimize_rules.use_eigen import UseEigenAttribute
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.util.misc import mul


def generate_template(transpose_A, transpose_B):
    return """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    float *A = %%LOAD_BUFFER(A)%%;
    float *B = %%LOAD_BUFFER(B)%%;
    float *C = %%LOAD_BUFFER(C)%%;

    const int M = %%LOAD_BUFFER(M)%%;
    const int N = %%LOAD_BUFFER(N)%%;
    const int K = %%LOAD_BUFFER(K)%%;

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

def generate_template_eigen(transpose_A, transpose_B):
    return """
#ifndef INCLUDE_EIGEN
#define INCLUDE_EIGEN
#include <Eigen/Dense>
#endif

void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    float *A = %%LOAD_BUFFER(A)%%;
    float *B = %%LOAD_BUFFER(B)%%;
    float *C = %%LOAD_BUFFER(C)%%;

    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%A_MAJOR%%> > a_mat(A, %%LOAD_BUFFER(M)%%, %%LOAD_BUFFER(K)%%);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::%%B_MAJOR%%> > b_mat(B, %%LOAD_BUFFER(K)%%, %%LOAD_BUFFER(N)%%);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > c_mat(C, %%LOAD_BUFFER(M)%%, %%LOAD_BUFFER(N)%%);

    c_mat.noalias() = a_mat * b_mat;
}
""" \
        .replace("%%A_MAJOR%%", "RowMajor" if transpose_A else "ColMajor") \
        .replace("%%B_MAJOR%%", "RowMajor" if transpose_B else "ColMajor")


@WebassemblyDescriptorGenerator.register_handler(Tensordot)
def tensordot(op: Tensordot, memory_layout: MemoryLayout) -> List[Kernel]:
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]
    axes = op.axes

    # Reduced axes must be located on inside of input variables.
    assert A.order.axes[-len(axes[0]):] == axes[0]
    assert B.order.axes[-len(axes[1]):] == axes[1]

    # output variable's axes order must be as [*a_remained_axes, *b_remained_axes]
    assert C.order.axes[:A.ndim - len(axes[0])] == A.order.axes[:-len(axes[0])]
    assert C.order.axes[-(B.ndim - len(axes[1])):] == B.order.axes[:-len(axes[1])]
    assert C.ndim == A.ndim - len(axes[0]) + B.ndim - len(axes[1])

    K = mul(A.shape_dict[a] for a in axes[0])
    M = A.size // K
    N = B.size // K

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "A": memory_layout[A],
        "B": memory_layout[B],
        "C": memory_layout[C],
        "M": M,
        "N": N,
        "K": K
    })

    if op.has_attribute(UseEigenAttribute):
        source = generate_template_eigen(True, False)
        buffer_injector.register({
            "A": memory_layout[A],
            "B": memory_layout[B],
            "C": memory_layout[C]
        })

    else:
        source = generate_template(True, False)
        buffer_injector.register({
            "A": memory_layout[A],
            "B": memory_layout[B],
            "C": memory_layout[C],
            "M": M,
            "N": N,
            "K": K
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
