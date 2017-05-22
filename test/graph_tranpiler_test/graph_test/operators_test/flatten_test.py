from nose.tools import raises

from graph_transpiler.graph.axis import Axis
from graph_transpiler.graph.operators.flatten import Flatten
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderNC


def test_normal():
    x = Variable([2, 3, 4, 5], OrderNHWC)
    y, = Flatten(None, in_axes=[Axis.H, Axis.W, Axis.C], out_axis=Axis.C)(x)

    assert y.order == OrderNC
    assert y.shape == [2, 60]


@raises(ValueError)
def test_duplicate_axis():
    x = Variable([2, 3, 4, 5], OrderNHWC)
    y, = Flatten(None, in_axes=[Axis.H, Axis.W, Axis.C], out_axis=Axis.N)(x)


@raises(ValueError)
def test_no_contained_axis():
    x = Variable([2, 3], OrderNC)
    y, = Flatten(None, in_axes=[Axis.H, Axis.W, Axis.C], out_axis=Axis.C)(x)
