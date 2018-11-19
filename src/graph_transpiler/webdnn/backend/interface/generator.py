import copy
import sys
from collections import defaultdict
from typing import Generic, TypeVar, Type, Callable, List, Dict

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.optimizer.general_optimize_rule import GeneralOptimizeRule
from webdnn.util import console, flags

backend_names = ["webgpu", "webgl", "webassembly", "fallback"]

T_KERNEL = TypeVar("T_KERNEL")
T_EXEC_DATA = TypeVar("T_EXEC_DATA")


class DescriptorGenerator(Generic[T_KERNEL, T_EXEC_DATA]):
    _handler_map = defaultdict(dict)  # type: Dict[str, Dict[str, Callable[[Operator, MemoryLayout], List[T_KERNEL]]]]

    @classmethod
    def generate(cls, graph: Graph, constant_encoder_name: str = None) -> T_EXEC_DATA:
        raise NotImplementedError

    @classmethod
    def register_handler(cls, OperatorClass: Type[Operator]):
        """

        Returns:
            :
        """
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
                raise NotImplementedError(f"[{cls.__name__}] Operator {op} is not handled by any generator handler")

            kernels += cls._handler_map[cls.__name__][key](op, memory_layout)

        return kernels


def get_generator(backend: str):
    if backend == "webgpu":
        from webdnn.backend.webgpu.generator import generate as generate_webgpu
        return generate_webgpu
    elif backend == "webgl":
        from webdnn.backend.webgl.generator import generate as generate_webgl
        return generate_webgl
    elif backend == "webassembly":
        from webdnn.backend.webassembly.generator import generate as generate_webassembly
        return generate_webassembly
    elif backend == "fallback":
        from webdnn.backend.fallback.generator import generate as generate_fallback
        return generate_fallback
    else:
        raise NotImplementedError(f"Unknown backend: {backend}")


def generate_descriptor(backend: str, graph: Graph, **kwargs) -> IGraphExecutionData:
    """generate_descriptor(backend, graph, **kwargs)

    This is utility function to generate graph descriptor. This function create specified backend descriptor generator and generat graph
    descriptor.

    Args:
        backend (str): target backend
        graph (:class:`~webdnn.Graph`): graph

    Returns:
        (:class:`~webdnn.backend.interface.graph_descriptor.IGraphExecutionData`) generated graph descriptor
    """

    result = []
    error = []

    # run on thread which have large stack
    def worker():
        try:
            generator = get_generator(backend)

            # Graph is transformed by backend-specific optimization
            c_graph = copy.deepcopy(graph)

            # some optimize rule work even when OPTIMIZE=0
            opt_graph, _ = GeneralOptimizeRule().optimize(c_graph)

            result.append(generator(opt_graph, **kwargs))
        except Exception as ex:
            error.append(ex)

    if flags.NO_WORKER_THREAD:
        worker()
    else:
        import threading
        sys.setrecursionlimit(16384)
        threading.stack_size(64 * 1024 * 1024)
        t = threading.Thread(target=worker)
        t.start()
        t.join()
    if len(error) > 0:
        raise error[0]
    return result[0]
