import chainer.computational_graph

from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.order import OrderNC, OrderCN


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Neg")
def _convert_neg(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Neg):
    x = converter.get_variable(c_op.inputs[0])
    y = -x
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Absolute")
def _convert_absolute(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Absolute):
    x = converter.get_variable(c_op.inputs[0])
    # noinspection PyTypeChecker
    y = abs(x)
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Add")
def _convert_add(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Add):
    x0 = converter.get_variable(c_op.inputs[0])
    x1 = converter.get_variable(c_op.inputs[1])
    y = x0 + x1
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("AddConstant")
def _convert_add_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.AddConstant):
    x = converter.get_variable(c_op.inputs[0])
    y = x + c_op.value
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Sub")
def _convert_sub(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Sub):
    x0 = converter.get_variable(c_op.inputs[0])
    x1 = converter.get_variable(c_op.inputs[1])
    y = x0 - x1
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("SubFromConstant")
def _convert_sub_from_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.SubFromConstant):
    x = converter.get_variable(c_op.inputs[0])
    y = c_op.value - x
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("Mul")
def _convert_mul(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Mul):
    x0 = converter.get_variable(c_op.inputs[0])
    x1 = converter.get_variable(c_op.inputs[1])
    y = x0 * x1
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("MulConstant")
@ChainerConverter.register_handler("MatMulVarConst")
@ChainerConverter.register_handler("MatMulConstVar")
def _convert_mul_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.MulConstant):
    x = converter.get_variable(c_op.inputs[0])
    y = c_op.value * x
    converter.set_variable(c_op.outputs[0](), y)


@ChainerConverter.register_handler("MatMulVarVar")
def _convert_mul(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Mul):
    x1 = converter.get_variable(c_op.inputs[0])
    x2 = converter.get_variable(c_op.inputs[1])

    x1, = ReinterpretAxis(None, x1.order, OrderNC)(x1)
    x2, = ReinterpretAxis(None, x2.order, OrderCN)(x2)

    y, = Linear(None)(x1, x2)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("Div")
def _convert_div(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Div):
    x0 = converter.get_variable(c_op.inputs[0])
    x1 = converter.get_variable(c_op.inputs[1])
    y = x0 / x1
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("DivFromConstant")
def _convert_div_from_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.DivFromConstant):
    x = converter.get_variable(c_op.inputs[0])
    y = c_op.value / x
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("PowVarVar")
def _convert_pow_var_var(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.PowVarVar):
    x0 = converter.get_variable(c_op.inputs[0])
    x1 = converter.get_variable(c_op.inputs[1])
    y = x0 ** x1
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("PowVarConst")
def _convert_pow_var_const(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.PowVarConst):
    x = converter.get_variable(c_op.inputs[0])
    y = x ** c_op.value
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal
@ChainerConverter.register_handler("PowConstVar")
def _convert_pow_const_var(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.PowConstVar):
    # TODO
    raise NotImplementedError("[ChainerConverter] PowConstVar is not supported")
