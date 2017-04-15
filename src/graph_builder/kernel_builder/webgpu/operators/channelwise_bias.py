from typing import List

from graph_builder.graph import Layer, Variable
from graph_builder.kernel_builder.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.kernel_builder.webgpu.kernel import Kernel
from graph_builder.kernel_builder.webgpu.operators.attributes import KBLayerAttribute
from graph_builder.kernel_builder.webgpu.operators.channelwise_weight import KBChannelwiseWeightOperator
from graph_builder.kernel_builder.webgpu.operators.layer import KBLayer, KBKernelSerialGenerator

channelwise_bias_source = """
float channelwise_bias(float x, float param)
{
    return x + param;
}
"""


class KBChannelwiseBiasLayer(KBLayer):
    def __init__(self, layer: Layer):
        super().__init__(layer, "bias", {KBLayerAttribute.Channelwise})

    def get_channelwise_operator(self,
                                 params_allocation: WorkspaceLayoutWebGPU,
                                 serial_generator: KBKernelSerialGenerator):
        allocation = params_allocation.allocationDict[self.layer.name + "/b"]
        return KBChannelwiseWeightOperator("channelwise_bias", {"channelwise_bias": channelwise_bias_source},
                                           serial_generator, allocation.offset)

    def generate_kernels(self,
                         batch_size: int,
                         bottoms: List[Variable], tops: List[Variable],
                         params_allocation: WorkspaceLayoutWebGPU,
                         variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        raise NotImplementedError()
