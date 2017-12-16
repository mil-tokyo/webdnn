import chainer

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.frontend.chainer.util import unary_op_handler, elementwise_binary_op_handler
from webdnn.frontend.util import check_broadcast_constraints
from webdnn.graph.operators.abs import Abs
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_div import ElementwiseDiv
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.elementwise_pow import ElementwisePow
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.order import Order
from webdnn.graph.variables.constant_variable import ConstantVariable


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Neg")
def _convert_neg(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.Neg"):
    x = converter.get_variable(c_op.inputs[0])
    y = -x
    converter.set_variable(c_op.outputs[0](), y)


ChainerConverter.register_handler("Absolute")(unary_op_handler(Abs))

ChainerConverter.register_handler("Add")(elementwise_binary_op_handler(ElementwiseAdd))


@ChainerConverter.register_handler("AddConstant")
def _convert_add_constant(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.AddConstant"):
    x = converter.get_variable(c_op.inputs[0])
    y = x + c_op.value
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Sub")
def _convert_sub(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.Sub"):
    x0 = converter.get_variable(c_op.inputs[0])
    x1 = converter.get_variable(c_op.inputs[1])
    check_broadcast_constraints(x0, x1)
    y = x0 - x1
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("SubFromConstant")
def _convert_sub_from_constant(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.SubFromConstant"):
    x = converter.get_variable(c_op.inputs[0])
    y = c_op.value - x
    converter.set_variable(c_op.outputs[0](), y)


ChainerConverter.register_handler("Mul")(elementwise_binary_op_handler(ElementwiseMul))


@ChainerConverter.register_handler("MulConstant")
def _convert_mul_constant(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.MulConstant"):
    x = converter.get_variable(c_op.inputs[0])
    y = c_op.value * x
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("MatMulVarConst")
def _convert_mat_mul_var_const(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.MatMulVarConst"):
    x1 = converter.get_variable(c_op.inputs[0])
    x2 = ConstantVariable(c_op.value, Order([None, None]))
    y, = Tensordot(None, axes=[x1.order.axes[1], x2.order.axes[0]])(x1, x2)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("MatMulConstVar")
def _convert_mat_mul_const_var(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.MatMulConstVar"):
    x1 = ConstantVariable(c_op.value, Order([None, None]))
    x2 = converter.get_variable(c_op.inputs[0])
    y, = Tensordot(None, axes=[x1.order.axes[1], x2.order.axes[0]])(x1, x2)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("MatMulVarVar")
def _convert_mat_mul_var_var(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.MatMulVarVar"):
    x1 = converter.get_variable(c_op.inputs[0])
    x2 = converter.get_variable(c_op.inputs[1])
    y, = Tensordot(None, axes=[x1.order.axes[1], x2.order.axes[0]])(x1, x2)
    converter.set_variable(c_op.outputs[0](), y)


ChainerConverter.register_handler("Div")(elementwise_binary_op_handler(ElementwiseDiv))


@ChainerConverter.register_handler("DivFromConstant")
def _convert_div_from_constant(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.DivFromConstant"):
    x = converter.get_variable(c_op.inputs[0])
    y = c_op.value / x
    converter.set_variable(c_op.outputs[0](), y)


ChainerConverter.register_handler("PowVarVar")(elementwise_binary_op_handler(ElementwisePow))


@ChainerConverter.register_handler("PowVarConst")
def _convert_pow_var_const(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.PowVarConst"):
    x = converter.get_variable(c_op.inputs[0])
    y = x ** c_op.value
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("PowConstVar")
def _convert_pow_const_var(converter: ChainerConverter, c_op: "chainer.functions.math.basic_math.PowConstVar"):
    # TODO
    raise NotImplementedError("[ChainerConverter] PowConstVar is not supported")
