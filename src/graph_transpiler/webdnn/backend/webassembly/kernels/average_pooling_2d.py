from typing import List

from webdnn.backend.webassembly.kernel import Kernel
from webdnn.backend.webassembly.kernels import util
from webdnn.backend.webassembly.meta_buffer_injector import MetaBufferInjector
from webdnn.backend.webgpu.allocator import MemoryLayout
from webdnn.graph.axis import Axis
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.order import OrderNHWC

template = """
void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(average_pooling_2d_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(average_pooling_2d_Y_offset)%%;
    const int N = %%META_LOAD(average_pooling_2d_N)%%;
    const int H1 = %%META_LOAD(average_pooling_2d_H1)%%;
    const int W1 = %%META_LOAD(average_pooling_2d_W1)%%;
    const int C = %%META_LOAD(average_pooling_2d_C)%%;
    const int H2 = %%META_LOAD(average_pooling_2d_H2)%%;
    const int W2 = %%META_LOAD(average_pooling_2d_W2)%%;
    const int K = %%META_LOAD(average_pooling_2d_K)%%;
    const int S = %%META_LOAD(average_pooling_2d_S)%%;
    const int P = %%META_LOAD(average_pooling_2d_P)%%;
    
    //%%INITIALIZER_ATTACHABLE_PLACEHOLDER%%

    for (int gid = 0; gid < N * H2 * W2 * C; gid += 1) {
        const int c = gid % C;
        const int w2 = gid / C % W2;
        const int h2 = gid / C / W2 % H2;
        const int n = gid / C / W2 / H2;

        float v = 0;
        for (int kh = 0; kh < K; kh++) {
            const int h1 = h2 * S - P + kh;
            if (h1 < 0 || h1 >= H1) continue;
            
            for (int kw = 0; kw < K; kw++) {
                const int w1 = w2 * S - P + kw;
                if (w1 < 0 || w1 >= W1) continue;

                v += X[((n * H1 + h1) * W1 + w1) * C + c];
            }
        }
        v /= K * K;

        //Y[gid] = %%CHANNELWISE_ATTACHABLE(v, n)%%;
        Y[gid] = v;
    }
}
"""


# noinspection PyUnusedLocal
def average_pooling_2d(op: AveragePooling2D,
                       constants_layout: MemoryLayout,
                       variables_layout: MemoryLayout,
                       metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.order == OrderNHWC
    assert y.variable.order == OrderNHWC

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "average_pooling_2d_X_offset": x.offset,
        "average_pooling_2d_Y_offset": y.offset,
        "average_pooling_2d_N": x.variable.shape_dict[Axis.N],
        "average_pooling_2d_H1": x.variable.shape_dict[Axis.H],
        "average_pooling_2d_W1": x.variable.shape_dict[Axis.W],
        "average_pooling_2d_C": x.variable.shape_dict[Axis.C],
        "average_pooling_2d_H2": y.variable.shape_dict[Axis.H],
        "average_pooling_2d_W2": y.variable.shape_dict[Axis.W],
        "average_pooling_2d_K": op.parameters["ksize"][0],
        "average_pooling_2d_S": op.parameters["stride"][0],
        "average_pooling_2d_P": op.parameters["padding"][0],
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("average_pooling_2d", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
