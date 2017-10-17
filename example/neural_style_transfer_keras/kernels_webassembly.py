from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from custom import UpSampling2D, Moment
from webdnn.graph.order import OrderNHWC

template_up_sampling = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(up_sampling_2d_X)%%;
    float *Y = %%LOAD_BUFFER(up_sampling_2d_Y)%%;
    const int N = %%LOAD_BUFFER(up_sampling_2d_N)%%;
    const int H1 = %%LOAD_BUFFER(up_sampling_2d_H1)%%;
    const int W1 = %%LOAD_BUFFER(up_sampling_2d_W1)%%;
    const int C = %%LOAD_BUFFER(up_sampling_2d_C)%%;
    const int H2 = %%LOAD_BUFFER(up_sampling_2d_H2)%%;
    const int W2 = %%LOAD_BUFFER(up_sampling_2d_W2)%%;
    const int KH = %%LOAD_BUFFER(up_sampling_2d_KH)%%;
    const int KW = %%LOAD_BUFFER(up_sampling_2d_KW)%%;

    for (int gid = 0; gid < N * H2 * W2 * C; gid += 1) {
        const int c = gid % C;
        const int w2 = gid / C % W2;
        const int h2 = gid / C / W2 % H2;
        const int n = gid / C / W2 / H2;

        const int h1 = h2 / KH;
        const int w1 = w2 / KW;
        Y[gid] = X[((n * H1 + h1) * W1 + w1) * C + c];
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(UpSampling2D)
def up_sampling_2d(op: UpSampling2D, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order == OrderNHWC
    assert y.order == OrderNHWC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "up_sampling_2d_X": memory_layout[x],
        "up_sampling_2d_Y": memory_layout[y],
        "up_sampling_2d_N": x.shape_dict[Axis.N],
        "up_sampling_2d_H1": x.shape_dict[Axis.H],
        "up_sampling_2d_W1": x.shape_dict[Axis.W],
        "up_sampling_2d_C": x.shape_dict[Axis.C],
        "up_sampling_2d_H2": y.shape_dict[Axis.H],
        "up_sampling_2d_W2": y.shape_dict[Axis.W],
        "up_sampling_2d_KH": op.parameters["size"][0],
        "up_sampling_2d_KW": op.parameters["size"][1],
    })

    name_injector = KernelNameInjector(op)

    source = template_up_sampling
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]


template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(moment_X)%%;
    float *Y_mean = %%LOAD_BUFFER(moment_Y_mean)%%;
    float *Y_inv_std = %%LOAD_BUFFER(moment_Y_inv_std)%%;
    const int N = %%LOAD_BUFFER(moment_N)%%;
    const int H = %%LOAD_BUFFER(moment_H)%%;
    const int W = %%LOAD_BUFFER(moment_W)%%;
    const int C = %%LOAD_BUFFER(moment_C)%%;
    const float eps = *((const float *)(& %%LOAD_BUFFER(moment_eps)%%));

    for (int gid = 0; gid < N * C; gid += 1) {
        const int c = gid % C;
        const int n = gid / C;
        
        float sum = 0.0;
        float sq_sum = 0.0;
        for (int y = 0; y < H; y++) {
            for (int x = 0; x < W; x++) {
                float v = X[((n * H + y) * W + x) * C + c];
                sum += v;
                sq_sum += v * v;
            }
        }
        
        float mean = sum / (H * W);
        float inv_std = 1.0 / sqrt(sq_sum / (H * W) - mean * mean + eps);
        Y_mean[gid] = mean;
        Y_inv_std[gid] = inv_std;
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(Moment)
def moment(op: Moment, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y_mean = op.outputs["y_mean"]
    y_inv_std = op.outputs["y_inv_std"]

    assert x.order == OrderNHWC
    assert y_mean.order == OrderNHWC
    assert y_inv_std.order == OrderNHWC

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "moment_X": memory_layout[x],
        "moment_Y_mean": memory_layout[y_mean],
        "moment_Y_inv_std": memory_layout[y_inv_std],
        "moment_N": x.shape_dict[Axis.N],
        "moment_H": x.shape_dict[Axis.H],
        "moment_W": x.shape_dict[Axis.W],
        "moment_C": x.shape_dict[Axis.C],
        "moment_eps": float(op.parameters["eps"])
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
