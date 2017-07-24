import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNC


@wrap_template
def template(axis=1, description: str = ""):
    vx = chainer.Variable(np.random.rand(2, 4))
    vy = chainer.functions.softmax(vx, axis)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.softmax {description}",
        graph=graph,
        inputs={x: np.transpose(vx.data, [OrderNC.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy.data, [OrderNC.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_axis_0():
    template(axis=0)
