"""
ONNX (https://github.com/onnx) Frontend
"""
from typing import Set, List, Union, Dict

from webdnn.frontend.converter import Converter
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
        graph = model.graph  # type: IGraphProto

        # Convert constant parameters
        for proto in graph.initializer:
            self.set_variable(proto.name, _convert_tensor_proto(proto))

        # Convert input variables
        # In ONNX, both input variable and parameters are included in `graph.input`.
        inputs = []
        for proto in filter(lambda proto: not self.has_variable(proto.name), graph.input):
            v = _convert_value_info_proto(proto)
            self.set_variable(proto.name, v)
            inputs.append(v)

        # Convert operators
        for onnx_op in _listup_functions(graph):
            self._convert_operator(onnx_op)

        graph = Graph(inputs, [self.get_variable(proto.name) for proto in graph.output])

        for v in graph.inputs:
            v.attributes.add(Input(v))

        for v in graph.outputs:
            v.attributes.add(Output(v))

        return graph

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

    data = np.frombuffer(proto.raw_data, np_type.type).reshape([1] if len(proto.dims) == 0 else proto.dims)
    return ConstantVariable(data, Order([None] * data.ndim))


def _convert_value_info_proto(proto: IValueInfoProto) -> Variable:
    """
    Convert ValueInfoProto into variable.
    """
    shape = [1] if len(proto.type.tensor_type.shape.dim) == 0 else [d.dim_value for d in proto.type.tensor_type.shape.dim]
    return Variable(shape, Order([None] * len(shape)))


def _listup_functions(graph: IGraphProto) -> Sequence[INodeProto]:
    _counter = 0

    class Container:
        """
        Proto object is not hashable. this container supports hash operation with proto object.
        """

        def __init__(self, proto: INodeProto):
            nonlocal _counter
            self.proto = proto
            self._hash = id(_counter)
            _counter += 1

        def __hash__(self):
            return self._hash

    stack = [proto.name for proto in graph.output]  # type: List[Union[Container, str]]
    resolved = {proto.name for proto in graph.input}  # type: Set[Union[Container, str]]
    result = []  # type: List[INodeProto]

    creator_map = {}
    for proto in graph.node:
        for name in proto.output:
            creator_map[name] = Container(proto)

    while len(stack) > 0:
        node = stack.pop()
        if node in resolved:
            continue

        if isinstance(node, str):
            # node is tensor's name
            prev_nodes = [] if node not in creator_map else [creator_map[node]]

        else:
            # node is container of operator proto
            prev_nodes = list(node.proto.input)

        unresolved_prevs = [prev_node for prev_node in prev_nodes if prev_node not in resolved]

        if len(unresolved_prevs) == 0:
            resolved.add(node)
            if not isinstance(node, str):
                result.append(node.proto)

        else:
            stack.append(node)
            stack += unresolved_prevs

    return result
