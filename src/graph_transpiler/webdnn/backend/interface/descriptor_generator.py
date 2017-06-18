from collections import defaultdict
from typing import Generic, TypeVar, Type, Callable, List, Dict

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.util import console

T_KERNEL = TypeVar("T_KERNEL")
T_EXEC_DATA = TypeVar("T_EXEC_DATA")


class DescriptorGenerator(Generic[T_KERNEL, T_EXEC_DATA]):
    _handler_map = defaultdict(dict)  # type: Dict[str, Dict[str, Callable[[Operator, MemoryLayout], List[T_KERNEL]]]]

    @classmethod
    def generate(cls, graph: Graph, constant_encoder_name: str = None) -> T_EXEC_DATA:
        raise NotImplementedError

    @classmethod
    def register_handler(cls, OperatorClass: Type[Operator]):
        key = OperatorClass.__name__

        def decorator(handler: Callable[[Operator, MemoryLayout], List[T_KERNEL]]):
            if key in cls._handler_map[cls.__name__]:
                console.warning(f"[{cls.__name__}] Generator handler of '{key}' is already registered and overwritten.")

            cls._handler_map[cls.__name__][key] = handler

        return decorator

    @classmethod
    def serialize_operator_type(cls, operator: Operator):
        return operator.__class__.__name__

    @classmethod
    def generate_kernels(cls, graph: Graph, memory_layout: MemoryLayout) -> List[T_KERNEL]:
        kernels = []  # Type: List[T_KERNEL]

        for op in traverse.listup_operators(graph):
            key = cls.serialize_operator_type(op)
            if key not in cls._handler_map[cls.__name__]:
                raise NotImplementedError(f"Operator {op} is not handled by any generator handler")

            kernels += cls._handler_map[cls.__name__][key](op, memory_layout)

        return kernels
