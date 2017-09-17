import numpy as np

from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.simplify_commutative_operator import SimplifyCommutativeOperator


def test_simple1():
    """
    before)

    c -[var0]-+
              +{Add}- y
    v -[var1]-+

    after)

    v -[var0]-+
              +{Add}- y
    c -[var1]-+
    """
    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c.shape, c.order)

    y = c + v
    op = y.output_from

    assert op.inputs["x0"] is c
    assert op.inputs["x1"] is v
    assert op.outputs["y"] is y

    SimplifyCommutativeOperator().optimize(Graph([v], [y]))

    assert op.inputs["x0"] is v
    assert op.inputs["x1"] is c
    assert op.outputs["y"] is y


def test_simple2():
    """
    before)

    v -[var0]-+
              +{Add}- y
    c -[var1]-+

    after) no changed

    v -[var0]-+
              +{Add}- y
    c -[var1]-+
    """
    c = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    v = Variable(c.shape, c.order)

    y = v + c
    op = y.output_from

    assert op.inputs["x0"] is v
    assert op.inputs["x1"] is c
    assert op.outputs["y"] is y

    SimplifyCommutativeOperator().optimize(Graph([v], [y]))

    assert op.inputs["x0"] is v
    assert op.inputs["x1"] is c
    assert op.outputs["y"] is y


def test_multiple():
    """
    before)

                      c2 -+
    c1 -[var0]-+          +-{op2}- y
               +{op1}- h -+
     v -[var1]-+

    after)

     v -[var0]-+
               +{op1}- h -+
    c1 -[var1]-+          +-{op2}- y
                      c2 -+
    """
    c1 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    c2 = c1.copy()
    v = Variable(c1.shape, c1.order)

    h = c1 + v
    op1 = h.output_from
    y = c2 + h
    op2 = y.output_from

    assert op1.inputs["x0"] is c1
    assert op1.inputs["x1"] is v
    assert op1.outputs["y"] is h
    assert op2.inputs["x0"] is c2
    assert op2.inputs["x1"] is h
    assert op2.outputs["y"] is y

    SimplifyCommutativeOperator().optimize(Graph([v], [y]))

    assert op1.inputs["x0"] is v
    assert op1.inputs["x1"] is c1
    assert op1.outputs["y"] is h
    assert op2.inputs["x0"] is h
    assert op2.inputs["x1"] is c2
    assert op2.outputs["y"] is y
