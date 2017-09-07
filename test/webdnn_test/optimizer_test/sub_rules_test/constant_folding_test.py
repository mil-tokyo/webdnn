import numpy as np

from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding


def test_fold_add():
    """
    before)

    c0 -+
        +{Add}-h1-+
    c1 -+         +-{Add}-h3
              h2-+

    after)

    c0+c1 -+
           +-{Add}-h3
       h2 -+
    """
    c0 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    c1 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)

    h1 = c0 + c1
    h2 = Variable([2, 3, 4, 5], OrderNCHW)

    h3 = h1 + h2

    graph = Graph([h2], [h3])

    ConstantFolding().optimize(graph)

    h1_new = h3.output_from.inputs["x0"]

    assert h1_new is not h1
    assert isinstance(h1_new, ConstantVariable)
    assert np.abs(np.mean(h1_new.data - (c0.data + c1.data))) < 1e-5


def test_fold_sub():
    c0 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    c1 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)

    h1 = c0 - c1
    h2 = Variable([2, 3, 4, 5], OrderNCHW)

    h3 = h1 + h2

    graph = Graph([h2], [h3])

    ConstantFolding().optimize(graph)

    h1_new = h3.output_from.inputs["x0"]

    assert h1_new is not h1
    assert isinstance(h1_new, ConstantVariable)
    assert np.abs(np.mean(h1_new.data - (c0.data - c1.data))) < 1e-5


def test_fold_mul():
    """
    before)

    c0 -+
        +{Mul}-h1-+
    c1 -+         +-{Add}-h3
               h2-+

    after)

    c0*c1 -+
           +-{Add}-h3
       h2 -+
    """
    c0 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    c1 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)

    h1 = c0 * c1
    h2 = Variable([2, 3, 4, 5], OrderNCHW)

    h3 = h1 + h2

    graph = Graph([h2], [h3])

    ConstantFolding().optimize(graph)

    h1_new = h3.output_from.inputs["x0"]

    assert h1_new is not h1
    assert isinstance(h1_new, ConstantVariable)
    assert np.abs(np.mean(h1_new.data - (c0.data * c1.data))) < 1e-5


def test_fold_mul_deep():
    """
    before)

    c0 -+
        +{Mul}-h1-+
    c1 -+         +-{Mul}-h2-+
               c2-+          +-{Add}-h4
                          h3-+
    after)

    c0*c1*c2 -+
              +-{Add}-h3
          h2 -+
    """
    c0 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)
    c1 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)

    h1 = c0 * c1
    c2 = ConstantVariable(np.random.rand(2, 3, 4, 5), OrderNCHW)

    h2 = h1 * c2
    h3 = Variable([2, 3, 4, 5], OrderNCHW)

    h4 = h2 + h3

    graph = Graph([h3], [h4])

    ConstantFolding().optimize(graph)

    h2_new = h4.output_from.inputs["x0"]

    assert h2_new is not h2
    assert isinstance(h2_new, ConstantVariable)
    assert np.abs(np.mean(h2_new.data - (c0.data * c1.data * c2.data))) < 1e-5
