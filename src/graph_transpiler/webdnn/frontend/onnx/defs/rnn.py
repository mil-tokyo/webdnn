"""
https://github.com/onnx/onnx/blob/09ada0f107f1cc1877f9194475c98d2d8512e188/onnx/defs/rnn/defs.cc
"""

from webdnn.frontend.onnx.converter import ONNXConverter
from webdnn.frontend.onnx.type_hint import INodeProto


@ONNXConverter.register_handler("RNN")
def _convert_rnn(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"RNN\" is not supported yet.")


@ONNXConverter.register_handler("GRU")
def _convert_random_gru(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"GRU\" is not supported yet.")


@ONNXConverter.register_handler("LSTM")
def _convert_lstm(converter: ONNXConverter, onnx_op: INodeProto):
    # FIXME: It's possible to support in current version of webdnn
    raise NotImplementedError("[ONNXConverter] Operator \"LSTM\" is not supported yet.")
