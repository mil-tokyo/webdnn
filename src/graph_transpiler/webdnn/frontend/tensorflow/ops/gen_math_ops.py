import numpy as np
import tensorflow as tf
from tensorflow.core.framework.types_pb2 import DT_FLOAT

from webdnn.frontend.tensorflow.converter import TensorFlowConverter
from webdnn.frontend.tensorflow.util import elementwise_binary_op_handler, unary_op_handler
from webdnn.frontend.util import check_broadcast_constraints
from webdnn.graph.operators.abs import Abs
from webdnn.graph.operators.acos import Acos
from webdnn.graph.operators.acosh import Acosh
from webdnn.graph.operators.asin import Asin
from webdnn.graph.operators.asinh import Asinh
from webdnn.graph.operators.atan import Atan
from webdnn.graph.operators.atanh import Atanh
from webdnn.graph.operators.cos import Cos
from webdnn.graph.operators.cosh import Cosh
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_div import ElementwiseDiv
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.elementwise_pow import ElementwisePow
from webdnn.graph.operators.exp import Exp
from webdnn.graph.operators.log import Log
from webdnn.graph.operators.max import Max
from webdnn.graph.operators.min import Min
from webdnn.graph.operators.prod import Prod
from webdnn.graph.operators.rsqrt import Rsqrt
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.select import Select
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.sin import Sin
from webdnn.graph.operators.sinh import Sinh
from webdnn.graph.operators.sum import Sum
from webdnn.graph.operators.tan import Tan
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.order import Order
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console

TensorFlowConverter.register_handler("Abs")(unary_op_handler(Abs))

TensorFlowConverter.register_handler("Acos")(unary_op_handler(Acos))

TensorFlowConverter.register_handler("Acosh")(unary_op_handler(Acosh))

TensorFlowConverter.register_handler("Add")(elementwise_binary_op_handler(ElementwiseAdd, ScalarAdd))

TensorFlowConverter.register_handler("AddN")(elementwise_binary_op_handler(ElementwiseAdd, ScalarAdd))


@TensorFlowConverter.register_handler("All")
def all_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Any")
def any_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ApproximateEqual")
def approximate_equal_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ArgMax")
def arg_max_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ArgMin")
def arg_min_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Asin")(unary_op_handler(Asin))

TensorFlowConverter.register_handler("Asinh")(unary_op_handler(Asinh))

TensorFlowConverter.register_handler("Atan")(unary_op_handler(Atan))


@TensorFlowConverter.register_handler("Atan2")
def atan2_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Atanh")(unary_op_handler(Atanh))


@TensorFlowConverter.register_handler("BatchMatMul")
def batch_mat_mul_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Betainc")
def betainc_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Bincount")
def bincount_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Bucketize")
def bucketize_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Cast")
def cast_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    dst_t = tf_op.get_attr("DstT")

    if dst_t != DT_FLOAT:
        console.warning("[TensorFlowConverter] Operator 'Cast' is ignored.")

    x = converter.get_variable(tf_op.inputs[0])
    converter.set_variable(tf_op.outputs[0], x)


@TensorFlowConverter.register_handler("Ceil")
def ceil_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Complex")
def complex_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ComplexAbs")
def complex_abs_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Conj")
def conj_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Cos")(unary_op_handler(Cos))

TensorFlowConverter.register_handler("Cosh")(unary_op_handler(Cosh))


@TensorFlowConverter.register_handler("Cross")
def cross_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Cumprod")
def cumprod_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Cumsum")
def cumsum_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Digamma")
def digamma_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Div")(elementwise_binary_op_handler(ElementwiseDiv))


@TensorFlowConverter.register_handler("Equal")
def equal_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Erf")
def erf_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Erfc")
def erfc_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Exp")(unary_op_handler(Exp))


@TensorFlowConverter.register_handler("Expm1")
def expm1_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    console.warning(
        "[TensorFlowConverter] In WebDNN, \"Expm1(x)\" is converted into \"Exp(x)-1\", which is not enough accurate as Expm1 when"
        "x is so small that \"Exp(x) == 1\" in floating point accuracy.")
    x = converter.get_variable(tf_op.inputs[0])
    y = Exp(None)(x)[0] - 1
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Floor")
def floor_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FloorDiv")
def floor_div_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("FloorMod")
def floor_mod_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Greater")
def greater_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(x, y)

    z = x > y
    converter.set_variable(tf_op.outputs[0], z)


@TensorFlowConverter.register_handler("GreaterEqual")
def greater_equal_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(x, y)

    z = x >= y
    converter.set_variable(tf_op.outputs[0], z)


@TensorFlowConverter.register_handler("Igamma")
def igamma_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Igammac")
def igammac_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Imag")
def imag_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Inv")
def inv_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = 1 / x
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("InvGrad")
def inv_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("IsFinite")
def is_finite_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("IsInf")
def is_inf_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("IsNan")
def is_nan_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Less")
def less_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(x, y)

    z = y > x
    converter.set_variable(tf_op.outputs[0], z)


@TensorFlowConverter.register_handler("LessEqual")
def less_equal_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(x, y)

    z = y >= x
    converter.set_variable(tf_op.outputs[0], z)


@TensorFlowConverter.register_handler("Lgamma")
def lgamma_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("LinSpace")
def lin_space_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Log")
def log_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y, = Log(None)(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Log1p")
def log1p_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    console.warning(
        "[TensorFlowConverter] In WebDNN, \"Log1p(x)\" is converted into \"Log(1+x)\", which is not enough accurate as Log1p when"
        "x is so small that \"1 + x == 1\" in floating point accuracy.")
    x = converter.get_variable(tf_op.inputs[0])
    y, = Log(None)(1 + x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("LogicalAnd")
def logical_and_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("LogicalNot")
def logical_not_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("LogicalOr")
def logical_or_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("MatMul")
def matmul_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    a = converter.get_variable(tf_op.inputs[0])
    b = converter.get_variable(tf_op.inputs[1])
    transposed_a = tf_op.get_attr("transpose_a")
    transposed_b = tf_op.get_attr("transpose_b")

    if a.ndim > 2 or b.ndim > 2:
        raise NotImplementedError("[TensorFlowConverter] Currently, MatMul is supported only 2D * 2D case.")

    reduced_axes = []
    if transposed_a:
        reduced_axes.append(a.order.axes[0])

    else:
        reduced_axes.append(a.order.axes[1])

    if transposed_b:
        reduced_axes.append(b.order.axes[1])

    else:
        reduced_axes.append(b.order.axes[0])

    c, = Tensordot(None, axes=reduced_axes)(a, b)
    converter.set_variable(tf_op.outputs[0], c)


@TensorFlowConverter.register_handler("Max")
def max_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    axis = converter.get_variable(tf_op.inputs[1])
    assert isinstance(axis, ConstantVariable), "[TensorFlowConverter] Operation 'Max' with dynamic axis  is not supported yet."

    for axis in [x.order.axes[i] for i in axis.data.astype(int).flatten().tolist()]:
        x, = Max(None, axis=axis)(x)

        if not tf_op.get_attr("keep_dims") and x.ndim > 1:
            x = x.squeeze(axis)

    converter.set_variable(tf_op.outputs[0], x)


@TensorFlowConverter.register_handler("Maximum")
def maximum_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(x, y)

    tmp = x > y
    z = x * tmp + y * (1 - tmp)
    converter.set_variable(tf_op.outputs[0], z)


@TensorFlowConverter.register_handler("Mean")
def mean_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Min")
def min_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    axis = converter.get_variable(tf_op.inputs[1])
    assert isinstance(axis, ConstantVariable), "[TensorFlowConverter] Operation 'Min' with dynamic axis  is not supported yet."

    for axis in [x.order.axes[i] for i in axis.data.astype(int).flatten().tolist()]:
        x, = Min(None, axis=axis)(x)

        if not tf_op.get_attr("keep_dims") and x.ndim > 1:
            x = x.squeeze(axis)

    converter.set_variable(tf_op.outputs[0], x)


@TensorFlowConverter.register_handler("Minimum")
def minimum_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(x, y)

    tmp = x > y
    z = x * (1 - tmp) + y * tmp
    converter.set_variable(tf_op.outputs[0], z)


@TensorFlowConverter.register_handler("Mod")
def mod_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Mul")(elementwise_binary_op_handler(ElementwiseMul, ScalarMul))


@TensorFlowConverter.register_handler("Neg")
def neg_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = -x
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("NotEqual")
def not_equal_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Polygamma")
def polygamma_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Pow")(elementwise_binary_op_handler(ElementwisePow))


@TensorFlowConverter.register_handler("Prod")
def prod_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    axis = converter.get_variable(tf_op.inputs[1])
    assert isinstance(axis, ConstantVariable), "[TensorFlowConverter] Operation 'Prod' with dynamic axis  is not supported yet."

    for axis in [x.order.axes[i] for i in axis.data.astype(int).flatten().tolist()]:
        x, = Prod(None, axis=axis)(x)

        if not tf_op.get_attr("keep_dims") and x.ndim > 1:
            x = x.squeeze(axis)

    converter.set_variable(tf_op.outputs[0], x)


@TensorFlowConverter.register_handler("QuantizeDownAndShrinkRange")
def quantize_down_and_shrink_range_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedAdd")
def quantized_add_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedMatMul")
def quantized_mat_mul_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("QuantizedMul")
def quantized_mul_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Range")
def range_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    start = converter.get_variable(tf_op.inputs[0])
    limit = converter.get_variable(tf_op.inputs[1])
    delta = converter.get_variable(tf_op.inputs[2])

    if not isinstance(start, ConstantVariable):
        raise NotImplementedError("[TensorFlowConverter] 'Range' operator with dynamic range is not supported yet")

    if not isinstance(limit, ConstantVariable):
        raise NotImplementedError("[TensorFlowConverter] 'Range' operator with dynamic range is not supported yet")

    if not isinstance(delta, ConstantVariable):
        raise NotImplementedError("[TensorFlowConverter] 'Range' operator with dynamic range is not supported yet")

    start = start.data.flatten()[0]
    limit = limit.data.flatten()[0]
    delta = delta.data.flatten()[0]

    y = ConstantVariable(np.arange(start, limit, delta), Order([None]))
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("Real")
def real_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("RealDiv")(elementwise_binary_op_handler(ElementwiseDiv))


@TensorFlowConverter.register_handler("Reciprocal")
def reciprocal_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("ReciprocalGrad")
def reciprocal_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("RequantizationRange")
def requantization_range_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Requantize")
def requantize_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Rint")
def rint_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Round")
def round_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Rsqrt")
def rsqrt_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y, = Rsqrt(None)(x)
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("RsqrtGrad")
def rsqrt_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SegmentMax")
def segment_max_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SegmentMean")
def segment_mean_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SegmentMin")
def segment_min_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SegmentProd")
def segment_prod_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SegmentSum")
def segment_sum_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Select")
def select_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    cond = converter.get_variable(tf_op.inputs[0])
    x1 = converter.get_variable(tf_op.inputs[1])
    x2 = converter.get_variable(tf_op.inputs[2])

    check_broadcast_constraints(cond, x1)
    check_broadcast_constraints(cond, x2)
    check_broadcast_constraints(x1, x2)

    y, = Select(None)(cond, x1, x2)
    converter.set_variable(tf_op.outputs[0], y)


TensorFlowConverter.register_handler("Sigmoid")(unary_op_handler(Sigmoid))


@TensorFlowConverter.register_handler("SigmoidGrad")
def sigmoid_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Sign")
def sign_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


TensorFlowConverter.register_handler("Sin")(unary_op_handler(Sin))

TensorFlowConverter.register_handler("Sinh")(unary_op_handler(Sinh))


@TensorFlowConverter.register_handler("SparseMatMul")
def sparse_mat_mul_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SparseSegmentMean")
def sparse_segment_mean_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SparseSegmentSqrtN")
def sparse_segment_sqrt_n_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SparseSegmentSum")
def sparse_segment_sum_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Sqrt")
def sqrt_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("SqrtGrad")
def sqrt_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Square")
def square_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = x ** 2
    converter.set_variable(tf_op.outputs[0], y)


@TensorFlowConverter.register_handler("SquaredDifference")
def squared_difference_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    y = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(x, y)

    converter.set_variable(tf_op.outputs[0], (x - y) ** 2)


@TensorFlowConverter.register_handler("Sub")
def sub_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    a = converter.get_variable(tf_op.inputs[0])
    b = converter.get_variable(tf_op.inputs[1])

    check_broadcast_constraints(a, b)

    c = a - b
    converter.set_variable(tf_op.outputs[0], c)


@TensorFlowConverter.register_handler("Sum")
def sum_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    x = converter.get_variable(tf_op.inputs[0])
    axis = converter.get_variable(tf_op.inputs[1])
    assert isinstance(axis, ConstantVariable), "[TensorFlowConverter] Operation 'Sum' with dynamic axis  is not supported yet."

    for axis in [x.order.axes[i] for i in axis.data.astype(int).flatten().tolist()]:
        x, = Sum(None, axis=axis)(x)

        if not tf_op.get_attr("keep_dims") and x.ndim > 1:
            x = x.squeeze(axis)

    converter.set_variable(tf_op.outputs[0], x)


TensorFlowConverter.register_handler("Tan")(unary_op_handler(Tan))

TensorFlowConverter.register_handler("Tanh")(unary_op_handler(Tanh))


@TensorFlowConverter.register_handler("TanhGrad")
def tanh_grad_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TruncateDiv")
def truncate_div_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("TruncateMod")
def truncate_mod_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("UnsortedSegmentMax")
def unsorted_segment_max_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("UnsortedSegmentSum")
def unsorted_segment_sum_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")


@TensorFlowConverter.register_handler("Zeta")
def zeta_handler(converter: TensorFlowConverter, tf_op: "tf.Operation"):
    raise NotImplementedError(f"[TensorFlowConverter] {tf_op.type} is not supported yet.")
