from typing import Generic, TypeVar, Iterable, Dict, Tuple, List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.graph.place_holder import PlaceHolder

T_KERNEL = TypeVar("T_KERNEL")


class IGraphDescriptor(Generic[T_KERNEL]):
    kernels: Iterable[T_KERNEL]
    unresolved_value_list: List[Tuple[int, PlaceHolder]]
    memory_layout: MemoryLayout
    licenses: Dict[str, str]


class IGraphExecutionData(Generic[T_KERNEL]):
    descriptor: IGraphDescriptor[T_KERNEL]
    constants: bytes
    backend_suffix: str

    def save(self, dirname: str):
        raise NotImplementedError()
