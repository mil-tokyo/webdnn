import warnings
from typing import Generic, TypeVar, Type, Callable, List, Dict

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator

T_KERNEL = TypeVar("T_KERNEL")
T_EXEC_DATA = TypeVar("T_EXEC_DATA")


class DescriptorGenerator(Generic[T_KERNEL, T_EXEC_DATA]):
    _handlers = {}  # type: Dict[Type[Operator], Callable[[Operator, MemoryLayout], List[T_KERNEL]]]

    @classmethod
    def generate(cls, graph: Graph, constant_encoder_name: str = None) -> T_EXEC_DATA:
        raise NotImplementedError

    @classmethod
    def register_generate_handler(cls, key: Type[Operator], handler: Callable[[Operator, MemoryLayout], List[T_KERNEL]]):
        if key in cls._handlers:
            warnings.warn(f"Generator handler of key '{key}' is already registered and overwritten.")

        cls._handlers[key] = handler

    @classmethod
    def generate_kernels(cls, graph: Graph, memory_layout: MemoryLayout) -> List[T_KERNEL]:
        kernels = []  # Type: List[T_KERNEL]

        for op in traverse.listup_operators(graph):
            key = op.__class__
            if key not in cls._handlers:
                raise KeyError(f"Operator {op} is not handled by any generator handler")

            kernels += cls._handlers[key](op, memory_layout)

        return kernels
