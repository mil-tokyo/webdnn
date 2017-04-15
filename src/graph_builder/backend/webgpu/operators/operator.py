import hashlib
from abc import abstractmethod
from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
from graph_builder.graph import Layer, Variable


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
    layer: Layer
    children: List["Operator"]
    inputs: List[Variable]
    outputs: List[Variable]

    def __init__(self,
                 layer: Layer,
                 inputs: List[Variable],
                 outputs: List[Variable]):
        self.layer = layer
        self.children = []
        self.inputs = inputs
        self.outputs = outputs

    @classmethod
    def add_canonical_suffix(cls, base_name: str, source: str):
        return f"{base_name}_{hashlib.sha224(source.encode('utf-8')).hexdigest()}"

    @abstractmethod
    def convert_to_kernels(self,
                           batch_size: int,
                           params_allocation: MemoryLayout,
                           variable_allocation: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        raise NotImplementedError
