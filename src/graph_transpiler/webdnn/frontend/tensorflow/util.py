import tensorflow as tf

from webdnn.frontend.tensorflow.converter import TensorFlowConverter
from webdnn.frontend.util import check_broadcast_constraints


def unary_op_handler(OperatorClass):
    def handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
        x = converter.get_variable(tf_op.inputs[0])
        y, = OperatorClass(None)(x)
        converter.set_variable(tf_op.outputs[0], y)

    return handler


def elementwise_binary_op_handler(OperatorClass):
    def handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
        a = converter.get_variable(tf_op.inputs[0])
        b = converter.get_variable(tf_op.inputs[1])

        # Broadcasting
        check_broadcast_constraints(a, b)

        c, = OperatorClass(None)(a, b)
        converter.set_variable(tf_op.outputs[0], c)

    return handler
