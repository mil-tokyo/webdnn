from typing import List

from graph_builder.backend.webassembly.allocator import MemoryLayout
from graph_builder.backend.webassembly.kernel import Kernel
from graph_builder.backend.webassembly.kernels import util
from graph_builder.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webassembly.operators.sgemm import Sgemm


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
            func_name: source
        },
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
