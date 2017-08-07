from itertools import permutations

from nose.tools import nottest

from test.util import assert_shape
from webdnn import Axis, Order, Variable
from webdnn.graph.axis import AxisKeyDict


@nottest
def template_test_unary_operator(OperatorClass, operator_kwargs=None, test1d=True, test2d=True, test3d=True, test4d=True,
                                 axes=None, orders=None, shape_dict=None, expected_dict=None):
    """
    Test template for unary operator

    Args:
        OperatorClass: Target operator class
        operator_kwargs: Operator keyword arguments
        test1d: If True, test with 1D input tensor is ran
        test2d: If True, test with 2D input tensor is ran
        test3d: If True, test with 3D input tensor is ran
        test4d: If True, test with 4D input tensor is ran
        orders: Orders for test input variable. If :code:`None`, all combination of axes are tested.
        axes: If specified and :code:`orders` is not specified, all combination of axes in :code:`axes` are tested.
        shape_dict: Input variable's shape
        expected_dict: Expected shape of output variable
    """

    if operator_kwargs is None:
        operator_kwargs = {}

    if axes is None:
        axes = [Axis.N, Axis.H, Axis.W, Axis.C, Axis.T]

    if orders is None:
        orders = []
        for ndim, flag in {1: test1d, 2: test2d, 3: test3d, 4: test4d}.items():
            if not flag:
                continue

            for axis in permutations(axes, ndim):
                orders.append(Order(axis))

    if shape_dict is None:
        shape_dict = AxisKeyDict()
        for i, axis in enumerate(axes):
            shape_dict[axis] = i + 5

    for order in orders:
        x = Variable([shape_dict[a] for a in order.axes], order)
        y, = OperatorClass(None, **operator_kwargs)(x)
        assert_shape(y, x.shape_dict if expected_dict is None else expected_dict)
