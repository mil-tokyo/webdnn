from typing import Set, List

from graph_builder.graph import Layer, Variable
from graph_builder.kernel_builder.webgpu.allocator_webgpu import WorkspaceLayoutWebGPU
from graph_builder.kernel_builder.webgpu.kernel import Kernel
from graph_builder.kernel_builder.webgpu.operators.attributes import KBLayerAttribute


class KBKernelSerialGenerator:
    """
    1カーネル内でユニークな変数suffixを作るためのカウンタ
    カーネル内だけでシリアルを作ることで、同じ組み合わせ(linear-bias)で同じカーネルソースになることを期待している
    """

    def __init__(self):
        self.value = 0

    def get(self):
        value = self.value
        self.value += 1
        return value


class KBLayer:
    layer: Layer
    name: str
    attributes: Set[KBLayerAttribute]
    children: List["KBLayer"]

    def __init__(self, layer: Layer, name: str, attributes: Set[KBLayerAttribute]):
        self.layer = layer
        self.name = name
        self.attributes = attributes

    def generate_kernels(self,
                         batch_size: int,
                         bottoms: List[Variable],
                         tops: List[Variable],
                         params_allocation: WorkspaceLayoutWebGPU,
                         variable_allocation: WorkspaceLayoutWebGPU) -> List[Kernel]:
        pass
