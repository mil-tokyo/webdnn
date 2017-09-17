import numpy as np

from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.simplify_associative_operator import SimplifyAssociativeOperatorLeftHand, \
    SimplifyAssociativeOperatorRightHand


def test_left_hand_without_folding():
    """test_left_hand_without_folding

    before)

    v1 -[x0]-+
             +{op1}- h -[x0]-+
     c -[x1]-+               +-{op2}- y
                             |
    v2 -----------------[x1]-+

    after)

     c ----------------------[x0]-+
                                  |
    v1 -[x0]-+                    +-{op1}- y
             +-{op2}- h_new -[x1]-+
    v2 -[x1]-+
    """
    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v1 = Variable(c.shape, c.order)
    v2 = Variable(c.shape, c.order)

    h = v1 + c
    op1 = h.output_from
    y = h + v2
    op2 = y.output_from

    SimplifyAssociativeOperatorLeftHand().optimize(Graph([v1, v2], [y]))

    assert op2.inputs["x0"] is v1
    assert op2.inputs["x1"] is v2
    assert op2.outputs["y"] is not h
    assert op1.inputs["x0"] is c
    assert op1.inputs["x1"] is op2.outputs["y"]
    assert op1.outputs["y"] is y


def test_left_hand_with_folding():
    """test_left_hand_with_folding

    before)

     v -[x0]-+
             +{op1}- h -[x0]-+
    c1 -[x1]-+               +-{op2}- y
                             |
    c2 -----------------[x1]-+

    after)

     v ----------------------[x0]-+
                                  |
    c1 -[x0]-+                    +-{op1}- y
             +-{op2}- h_new -[x1]-+
    c2 -[x1]-+
    """
    c1 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    c2 = c1.copy()
    v = Variable(c1.shape, c1.order)

    h = v + c1
    op1 = h.output_from
    y = h + c2
    op2 = y.output_from

    SimplifyAssociativeOperatorLeftHand().optimize(Graph([v], [y]))

    assert op2.inputs["x0"] is c1
    assert op2.inputs["x1"] is c2
    assert op2.outputs["y"] is not h
    assert op1.inputs["x0"] is v
    assert op1.inputs["x1"] is op2.outputs["y"]
    assert op1.outputs["y"] is y


def test_right_hand():
    """test_right_hand

    before)

    v1 -----------------[x0]-+
                             |
    v2 -[x0]-+               +-{op2}- y
             +{op1}- h -[x1]-+
     c -[x1]-+

    after)

    v1 -[x0]-+
             +{op2}- h_new -[x0]-+
    v2 -[x1]-+                   +-{op1}- y
                                 |
     c ---------------------[x1]-+
    """
    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v1 = Variable(c.shape, c.order)
    v2 = Variable(c.shape, c.order)

    h = v2 + c
    op1 = h.output_from
    y = v1 + h
    op2 = y.output_from

    SimplifyAssociativeOperatorRightHand().optimize(Graph([v1, v2], [y]))

    assert op2.inputs["x0"] is v1
    assert op2.inputs["x1"] is v2
    assert op2.outputs["y"] is not h
    assert op1.inputs["x0"] is op2.outputs["y"]
    assert op1.inputs["x1"] is c
    assert op1.outputs["y"] is y
