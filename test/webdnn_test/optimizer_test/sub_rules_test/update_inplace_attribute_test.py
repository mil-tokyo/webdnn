import numpy as np

from webdnn.graph.graph import Graph
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.order import OrderNCHW, OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.update_inplace_attribute import UpdateInplaceAttribute


def test_add_attribute():
    """
    test_add_attribute

    before)

    c -+
       +-{Add}- y
    v -+

    after)

    c -+
       +-{Add & Inplace}- y
    v -+
    """

    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c.shape, c.order)

    y = v + c
    op = y.output_from

    assert not op.has_attribute(Inplace)

    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert op.has_attribute(Inplace)


def test_remove():
    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c.shape, c.order)

    y = v + c
    op = y.output_from

    assert not op.has_attribute(Inplace)

    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert op.has_attribute(Inplace)

    v.change_order(OrderNHWC)
    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert not op.has_attribute(Inplace)


def test_no_change1():
    """
    test_no_change1

    c[OrderNCHW] -+
                  +-{Add}- y
    v[OrderNHWC] -+
    """

    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c.shape, c.order)

    v.change_order(OrderNHWC)

    y = c + v
    op = y.output_from

    assert not op.has_attribute(Inplace)

    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert not op.has_attribute(Inplace)


def test_no_change2():
    """
    test_no_change2

    before)

    c -+
       +-{Add}- y
    v -+

    after)

    c -+
       +-{Add & Inplace}- y
    v -+
    """

    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c.shape, c.order)

    y = v + c
    op = y.output_from

    assert not op.has_attribute(Inplace)

    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert op.has_attribute(Inplace)

    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert op.has_attribute(Inplace)


def test_input():
    """
    test_input

    v[Input] -+
              +-{Add}- y
           c -+
    """

    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c.shape, c.order)
    v.attributes.add(Input(v))

    y = v + c
    op = y.output_from

    assert not op.has_attribute(Inplace)

    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert not op.has_attribute(Inplace)


def test_constant():
    """
    test_constant

    c1 -+
        +-{Add}- h -+
    c2 -+           +- y
                 v -+
    """

    c1 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    c2 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c1.shape, c1.order)

    h = c1 + c2
    y = h + v
    op = h.output_from

    assert not op.has_attribute(Inplace)

    UpdateInplaceAttribute().optimize(Graph([v], [y]))

    assert not op.has_attribute(Inplace)
