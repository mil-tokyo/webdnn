import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.order import OrderNCHW, OrderC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.upgrade_operator_type import UpgradeOperatorType


def test_axiswise_bias():
    """
    before)

    b -+
       +-{AxiswiseBias}- y
    x -+

    after)

    b -+
       +-{ElementwiseAdd}- y
    x -+
    """

    b = ConstantVariable(np.random.rand(3), OrderC)
    x = Variable((2, 3, 4, 5), OrderNCHW)

    y, = AxiswiseBias(None, axis=Axis.C)(x, b)

    assert isinstance(y.output_from, AxiswiseBias)

    UpgradeOperatorType().optimize(Graph([x], [y]))

    assert isinstance(y.output_from, ElementwiseAdd)


def test_axiswise_scale():
    """
    before)

    s -+
       +-{AxiswiseScale}- y
    x -+

    after)

    s -+
       +-{ElementwiseMul}- y
    x -+
    """

    s = ConstantVariable(np.random.rand(3), OrderC)
    x = Variable((2, 3, 4, 5), OrderNCHW)

    y, = AxiswiseScale(None, axis=Axis.C)(x, s)

    assert isinstance(y.output_from, AxiswiseScale)

    UpgradeOperatorType().optimize(Graph([x], [y]))

    assert isinstance(y.output_from, ElementwiseMul)
