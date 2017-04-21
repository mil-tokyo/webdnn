from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.operators import Convolution2D
from graph_builder.graph.operators.attributes import Axis
from graph_builder.graph.variables import attributes as VA

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(convolution_2d_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(convolution_2d_Y_offset)%%;
    const device float *W = weight_buffer + %%META_LOAD(convolution_2d_W_offset)%%;

    const int N = %%META_LOAD(convolution_2d_N)%%;

    const int H1 = %%META_LOAD(convolution_2d_H1)%%;
    const int W1 = %%META_LOAD(convolution_2d_W1)%%;
    const int C1 = %%META_LOAD(convolution_2d_C1)%%;

    const int H2 = %%META_LOAD(convolution_2d_H2)%%;
    const int W2 = %%META_LOAD(convolution_2d_W2)%%;
    const int C2 = %%META_LOAD(convolution_2d_C2)%%;
    
    const int KH = %%META_LOAD(convolution_2d_KH)%%;
    const int KW = %%META_LOAD(convolution_2d_KW)%%;

    const int SH = %%META_LOAD(convolution_2d_SH)%%;
    const int SW = %%META_LOAD(convolution_2d_SW)%%;

    const int PH = %%META_LOAD(convolution_2d_PH)%%;
    const int PW = %%META_LOAD(convolution_2d_PW)%%;
    
    //%%INITIALIZER_ATTACHABLE_PLACEHOLDER%%

    for (int gid = index; gid < N * H2 * W2 * C2; gid += num_threads) {
        const int c2 = gid % C2;
        const int w2 = gid / C2 % W2;
        const int h2 = gid / C2 / W2 % H2;
        const int n = gid / C2 / W2 / H2;

        float sum = 0.0;
        for (int kh = 0; kh < KH; kh++) {
            const int h1 = h2 * SH - PH + kh;
            if (h1 < 0 || h1 >= H1) continue;
            
            for (int kw = 0; kw < KW; kw++) {
                const int w1 = w2 * SW - PW + kw;
                if (w1 < 0 || w1 >= W1) continue;

                for (int c1 = 0; c1 < C1; c1++) {
                    sum += X[((n * H1 + h1) * W1 + w1) * C1 + c1] * W[((kh * KW + kw) * C1 + c1) * C2 + c2];
                }
            }
        }

        //Y[gid] = %%CHANNELWISE_ATTACHABLE(sum, n)%%;
        Y[gid] = sum;
    }
}
"""


def convolution_2d(op: Convolution2D,
                   constants_layout: MemoryLayout,
                   variables_layout: MemoryLayout,
                   metabuffer_injector: MetaBufferInjector = None) -> List[Kernel]:
    x = variables_layout[op.inputs["x"]]
    w = constants_layout[op.inputs["w"]]
    y = variables_layout[op.outputs["y"]]

    assert x.variable.axis_order == VA.OrderNHWC, \
        f"[WebGPU] Convolution2D operator supports only OrderNHWC for data order of input variable. " + \
        f"Actual data order is {x.variable.axis_order}"

    assert w.variable.axis_order == VA.OrderHWCN, \
        f"[WebGPU] Convolution2D operator supports only OrderHWCN for data order of filter variable. " + \
        f"Actual data order is {w.variable.axis_order}"

    assert y.variable.axis_order == VA.OrderNHWC, \
        f"[WebGPU] Convolution2D operator supports only OrderNHWC for data order of output variable. " + \
        f"Actual data order is {y.variable.axis_order}"

    if metabuffer_injector is None:
        metabuffer_injector = MetaBufferInjector()

    metabuffer_injector.register({
        "convolution_2d_X_offset": x.offset,
        "convolution_2d_Y_offset": y.offset,
        "convolution_2d_W_offset": w.offset,
        "convolution_2d_N": x.variable.shape_dict[Axis.N],
        "convolution_2d_H1": x.variable.shape_dict[Axis.H],
        "convolution_2d_W1": x.variable.shape_dict[Axis.W],
        "convolution_2d_C1": x.variable.shape_dict[Axis.C],
        "convolution_2d_H2": y.variable.shape_dict[Axis.H],
        "convolution_2d_W2": y.variable.shape_dict[Axis.W],
        "convolution_2d_C2": y.variable.shape_dict[Axis.C],
        "convolution_2d_KH": op.KH,
        "convolution_2d_KW": op.KW,
        "convolution_2d_SH": op.SH,
        "convolution_2d_SW": op.SW,
        "convolution_2d_PH": op.PH,
        "convolution_2d_PW": op.PW
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("convolution_2d", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
