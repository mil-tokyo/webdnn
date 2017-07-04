import chainer.computational_graph

from webdnn.frontend.chainer import ChainerConverter
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.order import OrderNC, OrderCN


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("Neg")
def _convert_neg(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Neg):
    x = converter.get_variable(c_op.inputs[0])
    y, = ScalarAffine(None, scale=-1, bias=0)(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("Absolute")
def _convert_absolute(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Absolute):
    # FIXME: More effective implementation
    # abs(x) = ReLU(x) + ReLU(-x)

    x = converter.get_variable(c_op.inputs[0])

    y1, = Relu(None)(x)

    y2, = ScalarAffine(None, scale=-1, bias=0)(x)
    y2, = Relu(None)(y2)

    y, = ElementwiseSum(None)(y1, y2)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("Add")
def _convert_add(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Add):
    xs = [converter.get_variable(x) for x in c_op.inputs]

    n_opr = ElementwiseSum(None)

    y, = n_opr(*xs)

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("AddConstant")
def _convert_add_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.AddConstant):
    x = converter.get_variable(c_op.inputs[0])

    n_opr = ScalarAffine(None, scale=1, bias=float(c_op.value))

    y, = n_opr(x)

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("Sub")
def _convert_sub(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Sub):
    xs = [converter.get_variable(x) for x in c_op.inputs]
    assert len(xs) == 2, f"[ChainerConverter] len(xs)={len(xs)}"

    x1 = xs[0]
    x2, = ScalarAffine(None, scale=-1, bias=0)
    y, = ElementwiseSum(None)(x1, x2)

    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("SubFromConstant")
def _convert_sub_from_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.SubFromConstant):
    x = converter.get_variable(c_op.inputs[0])
    y, = ScalarAffine(None, scale=-1, bias=float(c_op.value))(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("Mul")
def _convert_mul(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Mul):
    x1 = converter.get_variable(c_op.inputs[0])
    x2 = converter.get_variable(c_op.inputs[1])

    y, = ElementwiseMul(None)(x1, x2)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("MulConstant")
@ChainerConverter.register_handler("MatMulVarConst")
@ChainerConverter.register_handler("MatMulConstVar")
def _convert_mul_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.MulConstant):
    x = converter.get_variable(c_op.inputs[0])
    y, = ScalarAffine(None, scale=float(c_op.value), bias=0.0)(x)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnresolvedReferences
@ChainerConverter.register_handler("MatMulVarVar")
def _convert_mul(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Mul):
    x1 = converter.get_variable(c_op.inputs[0])
    x2 = converter.get_variable(c_op.inputs[1])

    x1, = ReinterpretAxis(None, x1.order, OrderNC)(x1)
    x2, = ReinterpretAxis(None, x2.order, OrderCN)(x2)

    y, = Linear(None)(x1, x2)
    converter.set_variable(c_op.outputs[0](), y)


# noinspection PyUnusedLocal,PyUnresolvedReferences
@ChainerConverter.register_handler("Div")
def _convert_div(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.Div):
    # TODO
    raise NotImplementedError("[ChainerConverter] Div is not supported")


# noinspection PyUnresolvedReferences,PyUnusedLocal
@ChainerConverter.register_handler("DivFromConstant")
def _convert_div_from_constant(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.DivFromConstant):
    # TODO
    raise NotImplementedError("[ChainerConverter] DivFromConstant is not supported")


# noinspection PyUnresolvedReferences,PyUnusedLocal
@ChainerConverter.register_handler("PowVarVar")
def _convert_pow_var_var(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.PowVarVar):
    # TODO
    raise NotImplementedError("[ChainerConverter] PowVarVar is not supported")


# noinspection PyUnresolvedReferences,PyUnusedLocal
@ChainerConverter.register_handler("PowVarConst")
def _convert_pow_var_const(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.PowVarConst):
    # TODO
    raise NotImplementedError("[ChainerConverter] PowVarConst is not supported")


# noinspection PyUnresolvedReferences,PyUnusedLocal
@ChainerConverter.register_handler("PowConstVar")
def _convert_pow_const_var(converter: ChainerConverter, c_op: chainer.functions.math.basic_math.PowConstVar):
    # TODO
    raise NotImplementedError("[ChainerConverter] PowConstVar is not supported")
