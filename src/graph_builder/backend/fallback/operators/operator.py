import hashlib
from abc import abstractmethod
from typing import List

from graph_builder.backend.fallback.allocator import MemoryLayout
from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.frontend.graph import Operator, Variable


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
    name: str
    layer: Operator
    children: List["Operator"]
    inputs: List[Variable]
    outputs: List[Variable]

    def __init__(self,
                 layer: Operator,
                 inputs: List[Variable],
                 outputs: List[Variable]):
        self.layer = layer
        self.children = []
        self.inputs = inputs
        self.outputs = outputs

    @abstractmethod
    def convert_to_kernels(self,
                           batch_size: int) -> List[Kernel]:
        raise NotImplementedError
