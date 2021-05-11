import numpy as np
import onnx
from webdnn.model import Model, Graph, Variable, Operator, ConstantVariable

def _parse_node(node: onnx.NodeProto):
    pass

def _parse_graph(graph: onnx.GraphProto) -> Graph:
    pass

def parse_onnx(model: onnx.ModelProto) -> Model:
    opset_import_version = model.opset_import[0].version # type: int
    graph = _parse_graph(model.graph)
