"""
ONNX (https://github.com/onnx) Frontend
"""
from typing import List, Union, Dict, Tuple

from webdnn.frontend.converter import Converter, CyclicGraphError
from webdnn.frontend.onnx.type_hint import *
from webdnn.graph.graph import Graph
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console

FLAG_ONNX_INSTALLED = False
try:
    import onnx

    FLAG_ONNX_INSTALLED = True

except ImportError as e:
    console.debug("ONNX is not completely installed.")
    pass


def attribute_dict(proto: INodeProto) -> Dict[str, IAttributeProto]:
    return {attr.name: attr for attr in proto.attribute}


class ONNXConverter(Converter["onnx.NodeProto"]):
    """ONNXConverter()

    Converter for `Open Neural Network Exchange (ONNX) <http://onnx.ai/>`_.

    To use this converter, you need to install ONNX python module. see `ONNX github repository <https://github.com/onnx/onnx>`_.
    """

    opset_version: int  # ONNX operator set version

    def __init__(self):
        super(ONNXConverter, self).__init__()
        if not FLAG_ONNX_INSTALLED:
            raise ImportError("""
Module "onnx" cannot be imported. Please check that follow command works correctly.

    python -c "import onnx"

""")

    def serialize_operator_type(self, proto: INodeProto):
        return proto.op_type

    def convert(self, model: IModelProto) -> Graph:
        """convert(model)

        Convert ONNX computational graph into WebDNN IR.

        Args:
            model: Proto data of ONNX model

        .. admonition:: example

            Convert model stored as ONNX format in "model.proto".

            .. code::

                import onnx
                from webdnn.frontend.onnx import ONNXConverter

                # import model in onnx
                model = onnx.load("model.proto")

                # convert
                graph = ONNXConverter().convert(model)

        Returns:
            (:class:`~webdnn.Graph`): WebDNN Graph
        """
        onnx_graph = model.graph  # type: IGraphProto
        self.opset_version = model.opset_import[0].version

        # Convert constant parameters
        for proto in onnx_graph.initializer:
            self.set_variable(proto.name, _convert_tensor_proto(proto))

        # Convert input variables
        # In ONNX, both input variable and parameters are included in `graph.input`.
        inputs = []
        for proto in filter(lambda proto: not self.has_variable(proto.name), onnx_graph.input):
            v = _convert_value_info_proto(proto)
            self.set_variable(proto.name, v)
            inputs.append(v)

        # Convert operators
        for onnx_op in _listup_functions(onnx_graph):
            self._convert_operator(onnx_op)

        webdnn_graph = Graph(inputs, [self.get_variable(proto.name) for proto in onnx_graph.output])

        for v in webdnn_graph.inputs:
            v.attributes.add(Input())

        for v in webdnn_graph.outputs:
            v.attributes.add(Output())

        return webdnn_graph

    def _convert_operator(self, proto: INodeProto):
        console.debug(f"-----------------------------------------------------------")
        console.debug(f"Type  : {proto.op_type}")
        console.debug(f"Input : {proto.input}")
        console.debug(f"Output: {proto.output}")
        for name, val in attribute_dict(proto).items():
            console.debug(f"Attr  : {name} = {val}")

        super(ONNXConverter, self)._convert_operator(proto)


def _convert_tensor_proto(proto: ITensorProto) -> ConstantVariable:
    """
    Convert TensorProto into constant variable.
    """
    np_type = DataTypeMappingDict[proto.data_type]
    if np_type.type is None:
        raise TypeError(f"[ONNXConverter] type \"{np_type.name}\" is not supported")

    data = np.frombuffer(proto.raw_data, np_type.type).reshape(() if len(proto.dims) == 0 else proto.dims)
    return ConstantVariable(data, Order([None] * data.ndim))


def _convert_value_info_proto(proto: IValueInfoProto) -> Variable:
    """
    Convert ValueInfoProto into variable.
    """
    shape = [1] if len(proto.type.tensor_type.shape.dim) == 0 else [d.dim_value for d in
                                                                    proto.type.tensor_type.shape.dim]
    return Variable(shape, Order([None] * len(shape)))


def _listup_functions(graph: IGraphProto) -> Sequence[INodeProto]:
    class Container:
        """
        Proto object is not hashable. this container supports hash operation with proto object.
        """

        def __init__(self, proto: INodeProto):
            self.proto = proto

        def __hash__(self):
            return hash(self.proto.name)

        def __eq__(self, other):
            return isinstance(other, Container) and self.proto == other.proto

    creator_map = {}
    for proto in graph.node:
        for name in proto.output:
            creator_map[name] = Container(proto)

    def get_prev_nodes(node: Union[Container, str]) -> Sequence[Union[Container, str]]:
        nonlocal creator_map
        if node in graph.input:
            return []

        elif isinstance(node, Container):
            return node.proto.input

        else:
            return [] if node not in creator_map else [creator_map[node]]

    result = []  # type: List[Container]
    stack = [(node.name, None) for node in
             graph.output]  # type: List[Tuple[Union[Container, str], Union[Container, str]]]
    dependency_count = {}  # type: Dict[Union[Container, str], int]

    while len(stack) > 0:
        node_from, node_to = stack.pop()

        if node_from not in dependency_count:
            stack.append((node_from, node_to))

            prev_nodes = get_prev_nodes(node_from)
            dependency_count[node_from] = 0
            for prev_node in prev_nodes:
                if dependency_count.get(prev_node, 1) > 0:
                    dependency_count[node_from] += 1
                    stack.append((prev_node, node_from))

        elif dependency_count[node_from] == 0:
            if isinstance(node_from, Container):
                result.append(node_from)

            if node_to is not None:
                dependency_count[node_to] -= 1

        else:
            raise CyclicGraphError("[ONNXConverter] Cycles are detected")

    return [r.proto for r in result]
