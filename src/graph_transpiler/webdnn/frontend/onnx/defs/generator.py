"""
https://github.com/onnx/onnx/blob/09ada0f107f1cc1877f9194475c98d2d8512e188/onnx/defs/generator/defs.cc
"""
from webdnn.frontend.onnx.converter import ONNXConverter, attribute_dict
from webdnn.frontend.onnx.type_hint import *
from webdnn.graph.order import Order
from webdnn.graph.variables.constant_variable import ConstantVariable


@ONNXConverter.register_handler("Constant")
def _convert_constant(converter: ONNXConverter, onnx_op: INodeProto):
    attrs = attribute_dict(onnx_op)
    value = attrs["value"].t

    np_type = DataTypeMappingDict[value.data_type]
    if np_type.type is None:
        raise TypeError(f"[ONNXConverter] type \"{np_type.name}\" is not supported")
    # There may be scalar value, which is represented as 0-dim numpy array
    data = np.frombuffer(value.raw_data, np_type.type).reshape(() if len(value.dims) == 0 else value.dims)

    y = ConstantVariable(data, Order([None] * data.ndim))
    converter.set_variable(onnx_op.output[0], y)


@ONNXConverter.register_handler("RandomUniform")
def _convert_random_uniform(converter: ONNXConverter, onnx_op: INodeProto):
    raise NotImplementedError("[ONNXConverter] Operator \"RandomUniform\" is not supported yet.")


@ONNXConverter.register_handler("RandomNormal")
def _convert_random_normal(converter: ONNXConverter, onnx_op: INodeProto):
    raise NotImplementedError("[ONNXConverter] Operator \"RandomNormal\" is not supported yet.")


@ONNXConverter.register_handler("RandomUniformLike")
def _convert_random_uniform_like(converter: ONNXConverter, onnx_op: INodeProto):
    raise NotImplementedError("[ONNXConverter] Operator \"RandomUniformLike\" is not supported yet.")


@ONNXConverter.register_handler("RandomNormalLike")
def _convert_random_normal_like(converter: ONNXConverter, onnx_op: INodeProto):
    raise NotImplementedError("[ONNXConverter] Operator \"RandomNormalLike\" is not supported yet.")
