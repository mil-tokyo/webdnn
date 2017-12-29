import numpy as np
from nose.tools import raises

from webdnn.graph.axis import Axis
from webdnn.graph.operators.abs import Abs
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_div import ElementwiseDiv
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.elementwise_pow import ElementwisePow
from webdnn.graph.operators.greater import Greater
from webdnn.graph.operators.greater_equal import GreaterEqual
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.operators.scalar_pow import ScalarPow
from webdnn.graph.operators.slice import Slice
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.order import OrderNHWC, OrderHWCN, OrderNC, OrderCHWN, OrderCN, Order, OrderNCHW
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


def test_construction():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert v1.shape == (1, 2, 3, 4)
    assert v1.order == OrderNHWC


def test_size():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert v1.size == 1 * 2 * 3 * 4


def test_ndim():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert v1.ndim == 4


def test_shape_dict():
    v1 = Variable([1, 2, 3, 4], OrderNHWC)

    assert len(v1.shape_dict) == 4
    assert v1.shape_dict[Axis.N] == 1
    assert v1.shape_dict[Axis.H] == 2
    assert v1.shape_dict[Axis.W] == 3
    assert v1.shape_dict[Axis.C] == 4


def test_change_order():
    v = Variable([1, 2, 3, 4], OrderNHWC)
    v.change_order(OrderHWCN)

    assert v.order == OrderHWCN
    assert v.shape == (2, 3, 4, 1)


def test_change_order_with_expansion():
    v = Variable([3, 4], OrderNC)
    v.change_order(OrderCHWN)

    assert v.order == OrderCHWN
    assert v.shape == (4, 1, 1, 3)


def test_change_order_with_compression():
    v = Variable([3, 1, 1, 4], OrderNHWC)
    v.change_order(OrderCN)

    assert v.order == OrderCN
    assert v.shape == (4, 3)


@raises(AssertionError)
def test_change_order_with_invalid_compression():
    v = Variable([3, 2, 2, 4], OrderNHWC)
    v.change_order(OrderCN)


def test_copy():
    v1 = Variable([3, 2, 2, 4], OrderNHWC)
    v2 = v1.copy()

    assert v2.order == v1.order
    assert v2.parameters == v1.parameters
    assert all(v1.has_attribute(type(a)) for a in v2.attributes)


# unary operators

def test_pos():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = +v1

    assert isinstance(v2.output_from, ScalarMul)
    assert v2.output_from.value == 1
    assert v2.output_from.inputs["x0"] == v1


def test_neg():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = -v1

    assert isinstance(v2.output_from, ScalarMul)
    assert v2.output_from.value == -1
    assert v2.output_from.inputs["x0"] == v1


def test_abs():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = abs(v1)

    assert isinstance(v2.output_from, Abs)
    assert v2.output_from.inputs["x0"] == v1


# binary operators

# add

def test_add_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 + v2
    assert isinstance(v3.output_from, ElementwiseAdd)
    assert v3.output_from.inputs["x0"] == v1
    assert v3.output_from.inputs["x1"] == v2


def test_add_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 + 3
    assert isinstance(v2.output_from, ScalarAdd)
    assert v2.output_from.inputs["x0"] == v1
    assert v2.output_from.value == 3


@raises(TypeError)
def test_add_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) + "3"


def test_radd_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 3 + v1
    assert isinstance(v2.output_from, ScalarAdd)
    assert v2.output_from.inputs["x0"] == v1
    assert v2.output_from.value == 3


@raises(TypeError)
def test_radd_invalid_type():
    "3" + Variable([2, 3, 4, 5], OrderNHWC)


# sub

def test_sub_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 - v2
    assert isinstance(v3.output_from, ElementwiseAdd)
    assert v3.output_from.inputs["x0"] == v1
    neg_v2 = v3.output_from.inputs["x1"]
    assert isinstance(neg_v2.output_from, ScalarMul)
    assert neg_v2.output_from.inputs["x0"] == v2
    assert neg_v2.output_from.value == -1


def test_sub_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 - 3
    assert isinstance(v2.output_from, ScalarAdd)
    assert v2.output_from.inputs["x0"] == v1
    assert v2.output_from.value == -3


@raises(TypeError)
def test_sub_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) - "3"


def test_rsub_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 3 - v1
    assert isinstance(v2.output_from, ScalarAdd)
    assert v2.output_from.value == 3
    neg_v1 = v2.output_from.inputs["x0"]
    assert isinstance(neg_v1.output_from, ScalarMul)
    assert neg_v1.output_from.inputs["x0"] == v1


@raises(TypeError)
def test_rsub_invalid_type():
    "3" - Variable([2, 3, 4, 5], OrderNHWC)


# mul

def test_mul_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 * v2
    assert isinstance(v3.output_from, ElementwiseMul)
    assert v3.output_from.inputs["x0"] == v1
    assert v3.output_from.inputs["x1"] == v2


def test_mul_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 * 3
    assert isinstance(v2.output_from, ScalarMul)
    assert v2.output_from.inputs["x0"] == v1
    assert v2.output_from.value == 3


@raises(TypeError)
def test_mul_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) * "3"


def test_rmul_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 3 * v1
    assert isinstance(v2.output_from, ScalarMul)
    assert v2.output_from.inputs["x0"] == v1
    assert v2.output_from.value == 3


@raises(TypeError)
def test_rmul_invalid_type():
    "3" * Variable([2, 3, 4, 5], OrderNHWC)


# truediv

def test_truediv_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 / v2
    assert isinstance(v3.output_from, ElementwiseDiv)
    assert v3.output_from.inputs["x0"] == v1
    assert v3.output_from.inputs["x1"] == v2


def test_truediv_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 / 4
    assert isinstance(v2.output_from, ScalarMul)
    assert v2.output_from.inputs["x0"] == v1
    assert v2.output_from.value == 0.25


@raises(TypeError)
def test_truediv_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) / "3"


def test_rtruediv_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 4 / v1
    assert isinstance(v2.output_from, ScalarMul)
    assert v2.output_from.value == 4
    inv_v1 = v2.output_from.inputs["x0"]
    assert isinstance(inv_v1.output_from, ScalarPow)
    assert inv_v1.output_from.inputs["x0"] == v1
    assert inv_v1.output_from.value == -1


@raises(TypeError)
def test_rtruediv_invalid_type():
    "3" / Variable([2, 3, 4, 5], OrderNHWC)


# pow

def test_pow_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 ** v2
    assert isinstance(v3.output_from, ElementwisePow)
    assert v3.output_from.inputs["x0"] == v1
    assert v3.output_from.inputs["x1"] == v2


def test_pow_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 ** 4
    assert isinstance(v2.output_from, ScalarPow)
    assert v2.output_from.inputs["x0"] == v1
    assert v2.output_from.value == 4


@raises(TypeError)
def test_pow_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) ** "3"


def test_rpow_with_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 4 ** v1
    assert isinstance(v2.output_from, ElementwisePow)
    assert isinstance(v2.output_from.inputs["x0"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x0"].data == 4)
    assert v2.output_from.inputs["x1"] == v1


@raises(TypeError)
def test_rpow_invalid_type():
    "3" ** Variable([2, 3, 4, 5], OrderNHWC)


@raises(NotImplementedError)
def test_pow_modulo():
    Variable([2, 3, 4, 5], OrderNHWC).__pow__(2, 3)


# gt

def test_gt_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 > v2
    assert isinstance(v3.output_from, Greater)
    assert v3.output_from.inputs["x0"] == v1
    assert v3.output_from.inputs["x1"] == v2


def test_gt_variable_and_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 > 4
    assert isinstance(v2.output_from, Greater)
    assert v2.output_from.inputs["x0"] == v1
    assert isinstance(v2.output_from.inputs["x1"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x1"].data == 4)


def test_gt_scalar_and_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 4 > v1
    assert isinstance(v2.output_from, Greater)
    assert isinstance(v2.output_from.inputs["x0"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x0"].data == 4)
    assert v2.output_from.inputs["x1"] == v1


@raises(TypeError)
def test_gt_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) > "3"


# gte

def test_gte_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 >= v2
    assert isinstance(v3.output_from, GreaterEqual)
    assert v3.output_from.inputs["x0"] == v1
    assert v3.output_from.inputs["x1"] == v2


def test_gte_variable_and_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 >= 4
    assert isinstance(v2.output_from, GreaterEqual)
    assert v2.output_from.inputs["x0"] == v1
    assert isinstance(v2.output_from.inputs["x1"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x1"].data == 4)


def test_gte_scalar_and_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 4 >= v1
    assert isinstance(v2.output_from, GreaterEqual)
    assert isinstance(v2.output_from.inputs["x0"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x0"].data == 4)
    assert v2.output_from.inputs["x1"] == v1


@raises(TypeError)
def test_gte_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) >= "3"


# lt

def test_lt_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 < v2
    assert isinstance(v3.output_from, Greater)
    assert v3.output_from.inputs["x0"] == v2
    assert v3.output_from.inputs["x1"] == v1


def test_lt_variable_and_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 < 4
    assert isinstance(v2.output_from, Greater)
    assert isinstance(v2.output_from.inputs["x0"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x0"].data == 4)
    assert v2.output_from.inputs["x1"] == v1


def test_lt_scalar_and_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 4 < v1
    assert isinstance(v2.output_from, Greater)
    assert v2.output_from.inputs["x0"] == v1
    assert isinstance(v2.output_from.inputs["x1"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x1"].data == 4)


@raises(TypeError)
def test_lt_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) < "3"


# lte

def test_lte_with_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 3, 4, 5], OrderNHWC)
    v3 = v1 <= v2
    assert isinstance(v3.output_from, GreaterEqual)
    assert v3.output_from.inputs["x0"] == v2
    assert v3.output_from.inputs["x1"] == v1


def test_lte_variable_and_scalar():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1 <= 4
    assert isinstance(v2.output_from, GreaterEqual)
    assert isinstance(v2.output_from.inputs["x0"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x0"].data == 4)
    assert v2.output_from.inputs["x1"] == v1


def test_lte_scalar_and_variable():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = 4 <= v1
    assert isinstance(v2.output_from, GreaterEqual)
    assert v2.output_from.inputs["x0"] == v1
    assert isinstance(v2.output_from.inputs["x1"], ConstantVariable)
    assert np.all(v2.output_from.inputs["x1"].data == 4)


@raises(TypeError)
def test_lte_invalid_type():
    Variable([2, 3, 4, 5], OrderNHWC) <= "3"


def test_slice_with_ellipsis():
    v1 = Variable([2, 3, 4, 5, 6], Order([None, None, None, None, None]))
    v2 = v1[:, 2, ..., None, 2:4]
    assert v2.shape == (2, 4, 5, 1, 2), v2.shape
    assert v2.order.axes[0] == v1.order.axes[0]
    assert v2.order.axes[1] == v1.order.axes[2]
    assert v2.order.axes[2] == v1.order.axes[3]
    assert v2.order.axes[4] == v1.order.axes[4]
    assert isinstance(v2.output_from, Slice)


def test_slice_without_ellipsis():
    v1 = Variable([2, 3, 4, 5, 6], Order([None, None, None, None, None]))
    v2 = v1[:, 2, 3, :, None, 2:4]
    assert v2.shape == (2, 5, 1, 2), v2.shape
    assert v2.order.axes[0] == v1.order.axes[0]
    assert v2.order.axes[1] == v1.order.axes[3]
    assert v2.order.axes[3] == v1.order.axes[4]
    assert isinstance(v2.output_from, Slice)


@raises(TypeError)
def test_slice_invalid_type():
    v1 = Variable([2, 3, 4, 5, 6], Order([None, None, None, None, None]))
    v1[:, 2, 3, :, None, "hoge"]


def test_reshape():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1.reshape(shape=[1, 6, 4, 5], order=OrderNCHW)
    assert v2.shape_dict[Axis.N] == 1
    assert v2.shape_dict[Axis.C] == 6
    assert v2.shape_dict[Axis.H] == 4
    assert v2.shape_dict[Axis.W] == 5
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.inputs["x"] == v1


def test_expand_dims_with_index():
    v1 = Variable([2, 3], OrderNC)
    v2 = v1.expand_dims(Axis.H, 1)
    assert v2.order == Order([Axis.N, Axis.H, Axis.C])
    assert v2.shape_dict[Axis.N] == 2
    assert v2.shape_dict[Axis.H] == 1
    assert v2.shape_dict[Axis.C] == 3
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.inputs["x"] == v1


def test_expand_dims_without_index():
    v1 = Variable([2, 3], OrderNC)
    v2 = v1.expand_dims(Axis.H)
    assert v2.order == Order([Axis.N, Axis.C, Axis.H])
    assert v2.shape_dict[Axis.N] == 2
    assert v2.shape_dict[Axis.H] == 1
    assert v2.shape_dict[Axis.C] == 3
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.inputs["x"] == v1


def test_squeeze_with_one_axis():
    v1 = Variable([2, 1, 1, 3], OrderNHWC)
    v2 = v1.squeeze(Axis.H)
    assert v2.order == Order([Axis.N, Axis.W, Axis.C])
    assert v2.shape_dict[Axis.N] == 2
    assert v2.shape_dict[Axis.W] == 1
    assert v2.shape_dict[Axis.C] == 3
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.inputs["x"] == v1


def test_squeeze_with_axes():
    v1 = Variable([2, 1, 1, 3], OrderNHWC)
    v2 = v1.squeeze([Axis.H, Axis.W])
    assert v2.order == Order([Axis.N, Axis.C])
    assert v2.shape_dict[Axis.N] == 2
    assert v2.shape_dict[Axis.C] == 3
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.inputs["x"] == v1


def test_expand_dims_without_axis():
    v1 = Variable([2, 1, 1, 3], OrderNHWC)
    v2 = v1.squeeze()
    assert v2.order == Order([Axis.N, Axis.C])
    assert v2.shape_dict[Axis.N] == 2
    assert v2.shape_dict[Axis.C] == 3
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.inputs["x"] == v1


def test_combine_axes():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1.combine_axes([Axis.W, Axis.H], Axis.H)
    assert v2.order == Order([Axis.N, Axis.H, Axis.C])
    assert v2.shape_dict[Axis.N] == 2
    assert v2.shape_dict[Axis.H] == 12
    assert v2.shape_dict[Axis.C] == 5
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.in_order == Order([Axis.N, Axis.W, Axis.H, Axis.C])
    assert v2.output_from.out_order == Order([Axis.N, Axis.H, Axis.C])
    assert v2.output_from.inputs["x"] == v1


def test_combine_axes_create_new_axis():
    new_axis = Axis()
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1.combine_axes([Axis.W, Axis.H], new_axis)
    assert v2.order == Order([Axis.N, new_axis, Axis.C])
    assert v2.shape_dict[Axis.N] == 2
    assert v2.shape_dict[new_axis] == 12
    assert v2.shape_dict[Axis.C] == 5
    assert isinstance(v2.output_from, Reshape)
    assert v2.output_from.in_order == Order([Axis.N, Axis.W, Axis.H, Axis.C])
    assert v2.output_from.out_order == Order([Axis.N, new_axis, Axis.C])
    assert v2.output_from.inputs["x"] == v1


def test_reshape_like():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([1, 6, 4, 5], OrderNCHW)
    v3 = v1.reshape_like(v2)
    assert v3.shape_dict[Axis.N] == 1
    assert v3.shape_dict[Axis.C] == 6
    assert v3.shape_dict[Axis.H] == 4
    assert v3.shape_dict[Axis.W] == 5
    assert isinstance(v3.output_from, Reshape)
    assert v3.output_from.inputs["x"] == v1


def test_transpose():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1.transpose(OrderNCHW)
    assert v2.shape == (2, 5, 3, 4), v2.shape
    assert v2.order == OrderNCHW
    assert isinstance(v2.output_from, Transpose)
    assert v2.output_from.inputs["x0"] == v1


def test_transpose_like():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = Variable([2, 5, 3, 4], OrderNCHW)
    v3 = v1.transpose_like(v2)
    assert v3.shape == (2, 5, 3, 4), v3.shape
    assert v3.order == OrderNCHW
    assert isinstance(v3.output_from, Transpose)
    assert v3.output_from.inputs["x0"] == v1


def test_reinterpret_axes():
    v1 = Variable([2, 3, 4, 5], OrderNHWC)
    v2 = v1.reinterpret_axes(OrderNCHW)
    assert v2.shape == (2, 3, 4, 5), v2.shape
    assert v2.order == OrderNCHW
    assert isinstance(v2.output_from, ReinterpretAxis)
    assert v2.output_from.inputs["x"] == v1
