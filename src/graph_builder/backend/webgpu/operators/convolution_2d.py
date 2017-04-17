from typing import List

from graph_builder.backend.webgpu import attributes as A
from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel, GPUSize
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.backend.webgpu.operators.operator import Operator

convolution2d_source = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                          device float *data_buffer[[buffer(1)]],
                          const device int * %%META_NAME%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    device float *X = data_buffer + %%META_LOAD(input_data_offset)%%;
    device float *Y = data_buffer + %%META_LOAD(output_data_offset)%%;
    const device float *W = weight_buffer + %%META_LOAD(weight_data_offset)%%;

    const int N = %%META_LOAD(convolution_batchsize)%%;
    const int C1 = %%META_LOAD(convolution_c1)%%;
    const int C2 = %%META_LOAD(convolution_c2)%%;
    const int H1 = %%META_LOAD(convolution_h1)%%;
    const int W1 = %%META_LOAD(convolution_w1)%%;
    const int K = %%META_LOAD(convolution_ksize)%%;
    const int S = %%META_LOAD(convolution_stride)%%;
    const int P = %%META_LOAD(convolution_pad)%%;
    const int H2 = (H1+2*P - K) / S;
    const int W2 = (W1+2*P - K) / S;
    
    %%INITIALIZER_ATTACHABLE_PLACEHOLDER%%
  
    for (int gid = index; gid < N * H2 * W2 * C2; gid += num_threads) {
        
        int c2 = gid % C2;
        int w2 = gid / C2 % W2;
        int h2 = gid / C2 / W2 % H2;
        int n = gid / C2 / W2 / H2 % N;

        float result = 0.0;
        for (int kh = 0; kh < K; kh++) {
            const int h1 = h2 * S + kh - P;
            if (h1 < 0 || h1 >= H1) continue;
            
            for (int kw = 0; kw < K; kw++) {
                const int w1 = w2 * S + kw - P;
                if (w1 < 0 || w1 >= W1) continue;

                for (int c1 = 0; c1 < C1; c1++) {
                    result += W[((kh * K + kw) * C1 + c1) * C2 + c2] * X[((n * H1 + h1) * W1 + w1) * C1 + c1];
                }
            }
        }

        result = %%CHANNELWISE_ATTACHABLE(result, c2)%%;

        Y[((n * H2 + h2) * W2 + w2) * C2 + c2] = result;
    }
}
"""


class Convolution2D(Operator,
                    A.ChannelwiseAttachable,
                    A.InitializerAttachable):
    name: str = "convolution2d"

    def convert_to_kernels(self,
                           batch_size: int,
                           weights_layout: MemoryLayout,
                           variable_layout: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        input_var = variable_layout.allocation_dict[self.inputs[0].name]
        output_var = variable_layout.allocation_dict[self.outputs[0].name]
        weight_var = weights_layout.allocation_dict[self.layer.name + "/W"]

        metabuffer_injector.register({
            "input_data_offset": input_var.offset,
            "output_data_offset": output_var.offset,
            "weight_data_offset": weight_var.offset,
            "convolution_batchsize": batch_size,
            "convolution_h1": self.inputs[0].shape[1],
            "convolution_w1": self.inputs[0].shape[2],
            "convolution_c1": self.layer.parameters["in_size"],
            "convolution_c2": self.layer.parameters["out_size"],
            "convolution_ksize": self.layer.parameters["ksize"][0],
            "convolution_stride": self.layer.parameters["stride"][0],
            "convolution_pad": self.layer.parameters["pad"][0],
        })

        source = convolution2d_source
        source = self.apply_initializer_attach(metabuffer_injector, weights_layout, source)
        source = self.apply_channelwise_attach(source)
        source = metabuffer_injector.inject(source)

        func_name = Operator.add_canonical_suffix("convolution2d", source)

        source = source.replace("%%FUNC_NAME%%", func_name)

        kernel = Kernel(
            {func_name: source},
            func_name,
            GPUSize(8, 1, 1),
            GPUSize(512, 1, 1),
            metabuffer_injector.generate_buffer()
        )

        return [kernel]
