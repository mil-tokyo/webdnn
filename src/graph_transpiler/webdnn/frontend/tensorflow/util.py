import tensorflow as tf

from webdnn import ConstantVariable
from webdnn.frontend.tensorflow.converter import TensorFlowConverter
from webdnn.frontend.util import check_broadcast_constraints


def unary_op_handler(OperatorClass):
    def handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
        x = converter.get_variable(tf_op.inputs[0])
        y, = OperatorClass(None)(x)
        converter.set_variable(tf_op.outputs[0], y)

    return handler


def elementwise_binary_op_handler(OperatorClass, ScalarOperatorClass=None):
    def handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
        a = converter.get_variable(tf_op.inputs[0])
        b = converter.get_variable(tf_op.inputs[1])
        c = None
        if ScalarOperatorClass is not None:
            # Scalar operation if one of the input is constant and scalar
            if isinstance(a, ConstantVariable) and a.size == 1:
                c, = ScalarOperatorClass(None, value=float(a.data[0]))(b)
            elif isinstance(b, ConstantVariable) and b.size == 1:
                c, = ScalarOperatorClass(None, value=float(b.data[0]))(a)

        if c is None:
            # Broadcasting
            check_broadcast_constraints(a, b)

            c, = OperatorClass(None)(a, b)
        converter.set_variable(tf_op.outputs[0], c)

    return handler
