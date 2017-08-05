import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.util import check_broadcast_constraints


def unary_op_handler(OperatorClass):
    def handler(converter: ChainerConverter, c_op: "chainer.Function"):
        x = converter.get_variable(c_op.inputs[0])
        y, = OperatorClass(None)(x)
        converter.set_variable(c_op.outputs[0](), y)

    return handler


def elementwise_binary_op_handler(OperatorClass):
    def handler(converter: ChainerConverter, c_op: "chainer.Function"):
        a = converter.get_variable(c_op.inputs[0])
        b = converter.get_variable(c_op.inputs[1])

        # Broadcasting
        check_broadcast_constraints(a, b)

        c, = OperatorClass(None)(a, b)

        # Each chainer function holds output variables as weak reference
        converter.set_variable(c_op.outputs[0](), c)

    return handler
