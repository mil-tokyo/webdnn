from typing import List

from graph_builder.graph import Layer, LayerType, Variable
from graph_builder.backend.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.operators.channelwise_bias import ChannelwiseBias
from graph_builder.backend.webgpu.operators.linear import Linear
from graph_builder.backend.webgpu.operators.operator import Operator, SerialGenerator
from graph_builder.backend.webgpu.operators.relu import Relu


class KernelBuilder:
    @classmethod
    def build(cls,
              layer: Layer,
              batch_size: int,
              inputs: List[Variable],
              outputs: List[Variable],
              params_allocation: WorkspaceLayoutWebGPU,
              variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        operators = []  # type: List[Operator]
        serial_generator = SerialGenerator()

        for layer in layer.iterate_self_and_children():
            operators.append(cls._build_operator_single(layer, serial_generator))

        root_operator = operators.pop(0)
        root_operator.children = operators

        return root_operator.generate_kernels(
            batch_size,
            inputs,
            outputs,
            params_allocation,
            variable_allocation
        )

    @classmethod
    def _build_operator_single(cls, layer: Layer, serial_generator: SerialGenerator) -> Operator:
        if layer.layer_type == LayerType.Linear:
            return Linear(layer, serial_generator)

        elif layer.layer_type == LayerType.ChannelwiseBias:
            return ChannelwiseBias(layer, serial_generator)

        elif layer.layer_type == LayerType.Relu:
            return Relu(layer, serial_generator)

        else:
            raise NotImplementedError(f"layer type: {layer.layer_type}")
