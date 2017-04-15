from typing import List
from abc import abstractmethod
from graph_builder.graph import Layer, Variable
from graph_builder.backend.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.backend.webgpu.kernel import Kernel


class SerialGenerator:
    """
    1カーネル内でユニークな変数suffixを作るためのカウンタ
    カーネル内だけでシリアルを作ることで、同じ組み合わせ(linear-bias)で同じカーネルソースになることを期待している
    """

    def __init__(self):
        self.value = 0

    def __call__(self, prefix: str):
        value = self.value
        self.value += 1
        return prefix + str(value)


class Operator:
    layer: Layer
    name: str
    children: List["Operator"]

    def __init__(self,
                 layer: Layer,
                 serial_generator: SerialGenerator,
                 name: str = "layer"):
        self.layer = layer
        self.name = name

    @abstractmethod
    def generate_kernel_self(self,
                             batch_size: int,
                             inputs: List[Variable],
                             outputs: List[Variable],
                             params_allocation: WorkspaceLayoutWebGPU,
                             variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        raise NotImplementedError

    def generate_kernels(self,
                         batch_size: int,
                         inputs: List[Variable],
                         outputs: List[Variable],
                         params_allocation: WorkspaceLayoutWebGPU,
                         variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        kernels = self.generate_kernel_self(batch_size, inputs, outputs, params_allocation, variable_allocation)

        return kernels
