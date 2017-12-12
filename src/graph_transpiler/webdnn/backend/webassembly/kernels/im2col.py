from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.order import OrderNHWC, Order

template_NHWKKC = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *im = %%LOAD_BUFFER(im2col_im)%%;
    float *col = %%LOAD_BUFFER(im2col_col)%%;

    const int N = %%LOAD_BUFFER(im2col_N)%%;
    const int C1 = %%LOAD_BUFFER(im2col_C1)%%;
    const int H1 = %%LOAD_BUFFER(im2col_H1)%%;
    const int W1 = %%LOAD_BUFFER(im2col_W1)%%;
    const int H2 = %%LOAD_BUFFER(im2col_H2)%%;
    const int W2 = %%LOAD_BUFFER(im2col_W2)%%;
    const int KH = %%LOAD_BUFFER(im2col_KH)%%;
    const int KW = %%LOAD_BUFFER(im2col_KW)%%;
    const int DH = %%LOAD_BUFFER(im2col_DH)%%;
    const int DW = %%LOAD_BUFFER(im2col_DW)%%;
    const int SH = %%LOAD_BUFFER(im2col_SH)%%;
    const int SW = %%LOAD_BUFFER(im2col_SW)%%;
    const int PH = %%LOAD_BUFFER(im2col_PH)%%;
    const int PW = %%LOAD_BUFFER(im2col_PW)%%;

    for (int gid = 0; gid < N*H2*W2*KH*KW*C1; gid += 1) {
        const int c1 = gid % C1;
        const int kw = gid / C1 % KW;
        const int kh = gid / C1 / KW % KH;
        const int w2 = gid / C1 / KW / KH % W2;
        const int h2 = gid / C1 / KW / KH / W2 % H2;
        const int  n = gid / C1 / KW / KH / W2 / H2;

        const int h1 = h2 * SH - PH + kh * DH;
        const int w1 = w2 * SW - PW + kw * DW;

        col[gid] = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n*H1+h1)*W1+w1)*C1+c1];
    }
}
"""

template_KKCNHW = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *im = %%LOAD_BUFFER(im2col_im)%%;
    float *col = %%LOAD_BUFFER(im2col_col)%%;

    const int N = %%LOAD_BUFFER(im2col_N)%%;
    const int C1 = %%LOAD_BUFFER(im2col_C1)%%;
    const int H1 = %%LOAD_BUFFER(im2col_H1)%%;
    const int W1 = %%LOAD_BUFFER(im2col_W1)%%;
    const int H2 = %%LOAD_BUFFER(im2col_H2)%%;
    const int W2 = %%LOAD_BUFFER(im2col_W2)%%;
    const int KH = %%LOAD_BUFFER(im2col_KH)%%;
    const int KW = %%LOAD_BUFFER(im2col_KW)%%;
    const int DH = %%LOAD_BUFFER(im2col_DH)%%;
    const int DW = %%LOAD_BUFFER(im2col_DW)%%;
    const int SH = %%LOAD_BUFFER(im2col_SH)%%;
    const int SW = %%LOAD_BUFFER(im2col_SW)%%;
    const int PH = %%LOAD_BUFFER(im2col_PH)%%;
    const int PW = %%LOAD_BUFFER(im2col_PW)%%;

    for (int gid = 0; gid < N*H2*W2*KH*KW*C1; gid += 1) {
        const int w2 = gid % W2;
        const int h2 = gid / W2 % H2;
        const int  n = gid / W2 / H2 % N;
        const int c1 = gid / W2 / H2 / N % C1;
        const int kw = gid / W2 / H2 / N / C1 % KW;
        const int kh = gid / W2 / H2 / N / C1 / KW;

        const int h1 = h2 * SH - PH + kh * DH;
        const int w1 = w2 * SW - PW + kw * DW;

        col[gid] = (h1 < 0 || h1 >= H1 || w1 < 0 || w1 >= W1) ? 0 : im[((n*H1+h1)*W1+w1)*C1+c1];
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Im2Col)
def im2col(op: Im2Col, memory_layout: MemoryLayout) -> List[Kernel]:
    im = op.inputs["im"]
    col = op.outputs["col"]

    assert im.order == OrderNHWC
    col_acceptable_order = [
        Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C]),
        Order([Axis.KH, Axis.KW, Axis.C, Axis.N, Axis.H, Axis.W])
    ]
    assert col.order in col_acceptable_order

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "im2col_im": memory_layout[im],
        "im2col_col": memory_layout[col],
        "im2col_N": col.shape_dict[Axis.N],
        "im2col_C1": im.shape_dict[Axis.C],
        "im2col_H1": im.shape_dict[Axis.H],
        "im2col_W1": im.shape_dict[Axis.W],
        "im2col_H2": col.shape_dict[Axis.H],
        "im2col_W2": col.shape_dict[Axis.W],
        "im2col_KH": op.KH,
        "im2col_KW": op.KW,
        "im2col_DH": op.DH,
        "im2col_DW": op.DW,
        "im2col_SH": op.SH,
        "im2col_SW": op.SW,
        "im2col_PH": op.PH,
        "im2col_PW": op.PW,
    })

    name_injector = KernelNameInjector(op)

    source = template_KKCNHW if col.order == Order([Axis.KH, Axis.KW, Axis.C, Axis.N, Axis.H, Axis.W]) else template_NHWKKC
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
