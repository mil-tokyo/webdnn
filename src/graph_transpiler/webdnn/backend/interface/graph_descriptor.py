from typing import Generic, TypeVar, Iterable, Dict, Tuple, List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.graph.placeholder import Placeholder

T_KERNEL = TypeVar("T_KERNEL")


class IGraphDescriptor(Generic[T_KERNEL]):
    kernels: Iterable[T_KERNEL]
    unresolved_value_list: List[Tuple[int, Placeholder]]
    memory_layout: MemoryLayout
    licenses: Dict[str, str]


class IGraphExecutionData(Generic[T_KERNEL]):
    """
    Container class for graph descriptor and related datum.
    """

    def save(self, dirname: str):
        """save(dirname)

        Save graph descriptor and related files into specified directory.

        .. admonition:: Example

            .. code::

                descriptor = generate_descriptor("webgpu", graph)
                descriptor.save("./output")

        Args:
            dirname (str): destination directory name
        """
        raise NotImplementedError()
