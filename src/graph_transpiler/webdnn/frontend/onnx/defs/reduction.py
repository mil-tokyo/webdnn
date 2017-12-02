"""
https://github.com/onnx/onnx/blob/09ada0f107f1cc1877f9194475c98d2d8512e188/onnx/defs/reduction/defs.cc
"""

from webdnn.frontend.onnx.converter import ONNXConverter
from webdnn.frontend.onnx.type_hint import INodeProto


@ONNXConverter.register_handler("ReduceMax")
def _convert_reduce_max(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ReduceMax\" is not supported yet.")


@ONNXConverter.register_handler("ReduceMin")
def _convert_reduce_min(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ReduceMin\" is not supported yet.")


@ONNXConverter.register_handler("ReduceSum")
def _convert_reduce_sum(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ReduceSum\" is not supported yet.")


@ONNXConverter.register_handler("ReduceMean")
def _convert_reduce_mean(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ReduceMean\" is not supported yet.")


@ONNXConverter.register_handler("ReduceProd")
def _convert_reduce_prod(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ReduceProd\" is not supported yet.")


@ONNXConverter.register_handler("ReduceLogSumExp")
def _convert_reduce_logsumexp(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's easy to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ReduceLogSumExp\" is not supported yet.")


@ONNXConverter.register_handler("ArgMax")
def _convert_argmax(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ArgMax\" is not supported yet.")


@ONNXConverter.register_handler("ArgMin")
def _convert_argmin(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"ArgMin\" is not supported yet.")
