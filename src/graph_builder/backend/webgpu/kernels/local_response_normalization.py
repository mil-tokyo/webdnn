from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.kernels import util
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.local_response_normalization import LocalResponseNormalization
from graph_builder.graph.variables.attributes.order import OrderNHWC

template = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float *X = data_buffer + %%META_LOAD(local_response_normalization_X_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(local_response_normalization_Y_offset)%%;
    const int N = %%META_LOAD(local_response_normalization_N)%%;
    const int H = %%META_LOAD(local_response_normalization_H)%%;
    const int W = %%META_LOAD(local_response_normalization_W)%%;
    const int C = %%META_LOAD(local_response_normalization_C)%%;
    const int Phalfn = %%META_LOAD(local_response_normalization_param_half_n)%%;
    const float Pk = *((const device float *)(& %%META_LOAD(local_response_normalization_param_k)%%));
    const float Palpha = *((const device float *)(& %%META_LOAD(local_response_normalization_param_alpha)%%));
    const float Pmbeta = *((const device float *)(& %%META_LOAD(local_response_normalization_param_minus_beta)%%));
    
    //%%INITIALIZER_ATTACHABLE_PLACEHOLDER%%

    for (int gid = index; gid < N * H * W * C; gid += num_threads) {
        const int c = gid % C;
        const int w = gid / C % W;
        const int h = gid / C / W % H;
        const int n = gid / C / W / H;

        int ch_low = max(c - Phalfn, 0);
        int ch_high = min(c + Phalfn + 1, C);
        
        float sq_sum = 0.0;
        for (; ch_low < ch_high; ch_low++) {
            float val = X[((n * H + h) * W + w) * C + ch_low];
            sq_sum += val * val;
        }
        
        float scale = powr(sq_sum * Palpha + Pk, Pmbeta);
        float v = X[gid] * scale;
        
        //Y[gid] = %%CHANNELWISE_ATTACHABLE(v, n)%%;
        Y[gid] = v;
    }
}
"""


# noinspection PyUnusedLocal
def local_response_normalization(op: LocalResponseNormalization,
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
        "local_response_normalization_X_offset": x.offset,
        "local_response_normalization_Y_offset": y.offset,
        "local_response_normalization_N": x.variable.shape_dict[Axis.N],
        "local_response_normalization_H": x.variable.shape_dict[Axis.H],
        "local_response_normalization_W": x.variable.shape_dict[Axis.W],
        "local_response_normalization_C": x.variable.shape_dict[Axis.C],
        "local_response_normalization_param_half_n": int(op.parameters["n"] // 2),
        "local_response_normalization_param_k": float(op.parameters["k"]),
        "local_response_normalization_param_alpha": float(op.parameters["alpha"]),
        "local_response_normalization_param_minus_beta": float(-op.parameters["beta"])
    })

    source = metabuffer_injector.inject(template)
    func_name = util.add_canonical_suffix("local_response_normalization", source)
    source = source.replace("%%FUNC_NAME%%", func_name)

    kernel = Kernel(
        {func_name: source},
        func_name,
        GPUSize(8, 1, 1),
        GPUSize(1024, 1, 1),
        metabuffer_injector.generate_buffer()
    )

    return [kernel]
