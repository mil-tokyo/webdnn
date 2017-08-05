from test.util import assert_shape
from webdnn import Variable, Axis
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.order import OrderNC, OrderNT, OrderCN


def template(N=2, T=3, vocabulary_size=4, feature_size=5, order_x=OrderNT, order_w=OrderNC):
    x = Variable([N, T], OrderNT)
    w = Variable([feature_size, vocabulary_size], OrderNC)

    x.change_order(order_x)
    w.change_order(order_w)

    y, = Embedding(None)(x, w)

    assert_shape(y, AxisKeyDict([Axis.N, Axis.T, Axis.C], [N, T, feature_size]))


def test():
    template()


def test_feature_orderCN():
    template(order_w=OrderCN)
