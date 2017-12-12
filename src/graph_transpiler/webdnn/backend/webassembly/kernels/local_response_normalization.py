from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.order import OrderNHWC

template = """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    const float *X = %%LOAD_BUFFER(local_response_normalization_X)%%;
    float *Y = %%LOAD_BUFFER(local_response_normalization_Y)%%;
    const int N = %%LOAD_BUFFER(local_response_normalization_N)%%;
    const int H = %%LOAD_BUFFER(local_response_normalization_H)%%;
    const int W = %%LOAD_BUFFER(local_response_normalization_W)%%;
    const int C = %%LOAD_BUFFER(local_response_normalization_C)%%;
    const int Phalfn = %%LOAD_BUFFER(local_response_normalization_param_half_n)%%;
    const float Pk = *((const float *)(& %%LOAD_BUFFER(local_response_normalization_param_k)%%));
    const float Palpha = *((const float *)(& %%LOAD_BUFFER(local_response_normalization_param_alpha)%%));
    const float Pmbeta = *((const float *)(& %%LOAD_BUFFER(local_response_normalization_param_minus_beta)%%));

    for (int gid = 0; gid < N * H * W * C; gid += 1) {
        const int c = gid % C;
        const int w = gid / C % W;
        const int h = gid / C / W % H;
        const int n = gid / C / W / H;

        int ch_low = c - Phalfn;
        if (ch_low < 0) {
            ch_low = 0;
        }
        int ch_high = c + Phalfn + 1;
        if (ch_high > C) {
            ch_high = C;
        }

        float sq_sum = 0.0;
        for (; ch_low < ch_high; ch_low++) {
            float val = X[((n * H + h) * W + w) * C + ch_low];
            sq_sum += val * val;
        }

        float scale = powf(sq_sum * Palpha + Pk, Pmbeta);
        float v = X[gid] * scale;

        Y[gid] = v;
    }
}
"""


@WebassemblyDescriptorGenerator.register_handler(LocalResponseNormalization)
def local_response_normalization(op: LocalResponseNormalization, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    assert x.order == OrderNHWC, x.order
    assert y.order == OrderNHWC, y.order

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "local_response_normalization_X": memory_layout[x],
        "local_response_normalization_Y": memory_layout[y],
        "local_response_normalization_N": x.shape_dict[Axis.N],
        "local_response_normalization_H": x.shape_dict[Axis.H],
        "local_response_normalization_W": x.shape_dict[Axis.W],
        "local_response_normalization_C": x.shape_dict[Axis.C],
        "local_response_normalization_param_half_n": int(op.parameters["n"] // 2),
        "local_response_normalization_param_k": float(op.parameters["k"]),
        "local_response_normalization_param_alpha": float(op.parameters["alpha"]),
        "local_response_normalization_param_minus_beta": float(-op.parameters["beta"])
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
