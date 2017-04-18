import hashlib
from abc import abstractmethod
from typing import List

from graph_builder.backend.webgpu.allocator import MemoryLayout
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.backend.webgpu.meta_buffer_injector import MetaBufferInjector
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

    @classmethod
    def add_canonical_suffix(cls, base_name: str, source: str):
        return f"{base_name}_{hashlib.sha224(source.encode('utf-8')).hexdigest()}"

    @abstractmethod
    def convert_to_kernels(self,
                           batch_size: int,
                           weights_layout: MemoryLayout,
                           variable_layout: MemoryLayout,
                           metabuffer_injector: MetaBufferInjector) -> List[Kernel]:
        raise NotImplementedError

    def iter_children_all(self):
        class Iterator:
            children: List[Operator] = []

            def __init__(self, children):
                self.children += children

            def __iter__(self):
                return self

            def __next__(self) -> Operator:
                if len(self.children) == 0:
                    raise StopIteration()

                child = self.children.pop(0)
                self.children += child.children
                return child

        return Iterator(self.children)
