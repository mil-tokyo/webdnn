# Parses ONNX model into internal representation for optimization.
# TODO: implement them

from typing import Dict, List, Optional
import numpy as np
import onnx
from webdnn.util import make_random_identifier

def onnx_data_type_to_np(data_type: int):
    if data_type == onnx.TensorProto.FLOAT:
        return np.float32
    elif data_type == onnx.TensorProto.INT64:
        return np.int64
    elif data_type == onnx.TensorProto.INT32:
        return np.int32
    raise ValueError

class Variable:
    name: str
    dims: Optional[List[int]]# TODO: support dynamic shape
    data_type: Optional[int]# onnx.TensorProto.{FLOAT, INT64, ...}
    axis_order: Optional[List[int]]# for optimization
    input_to: List["Operator"]
    output_from: Optional["Operator"]

    def __init__(self, name: Optional[str], dims: Optional[List[int]], data_type: Optional[int], *, axis_order: Optional[List[int]]=None) -> None:
        self.name = name if name is not None else make_random_identifier()
        self.dims = dims
        self.data_type = data_type
        if axis_order is None:
            if dims is not None:
                axis_order = list(range(len(dims)))
        self.axis_order = axis_order
        self.input_to = []
        self.output_from = None
    
    @property
    def default_order(self) -> bool:
        raise NotImplementedError

class ConstantVariable(Variable):
    data: np.ndarray
    def __init__(self, dims: List[int], data_type: int, *, axis_order: Optional[List[int]]=None, data: Optional[np.ndarray]=None) -> None:
        super().__init__(dims, data_type, axis_order)
        if data is None:
            data = np.zeros(dims, dtype=onnx_data_type_to_np(data_type))
        self.data = data

class OperatorAttribute:
    f: Optional[float]
    i: Optional[int]
    s: Optional[str]
    t: ConstantVariable
    floats: Optional[List[float]]
    ints: Optional[List[int]]
    strings: Optional[List[str]]
    tensors: Optional[List[ConstantVariable]]
    # g, graphs is not supported

class Operator:
    name: str
    inputs: List[Variable]
    outputs: List[Variable]
    op_type: str
    domain: Optional[str]
    attributes: Dict[str, OperatorAttribute]

    def __init__(self, name: Optional[str], op_type: str, *, domain: Optional[str]=None, attributes: Optional[Dict[str, OperatorAttribute]]=None) -> None:
        self.name = name if name is not None else make_random_identifier()
        self.op_type = op_type
        self.domain = domain
        self.attributes = attributes if attributes is not None else {}
        self.inputs = []
        self.outputs = []

class Graph:
    operators: List[Operator]
    inputs: List[Variable]
    outputs: List[Variable]

    def __init__(self) -> None:
        self.operators = []
        self.inputs = []
        self.outputs = []

class Model:
    graph: Graph
    opset_import_version: int

    def __init__(self, graph: Graph, opset_import_version: int) -> None:
        self.graph = graph
        self.opset_import_version = opset_import_version
