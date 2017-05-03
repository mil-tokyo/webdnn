
from graph_builder.util import json


class IGraphDescriptor:
    pass


class IGraphExecutionData:
    descriptor: IGraphDescriptor
    constants: bytes
    backend_suffix: str

    def save(self, dirname: str):
        raise NotImplementedError()
