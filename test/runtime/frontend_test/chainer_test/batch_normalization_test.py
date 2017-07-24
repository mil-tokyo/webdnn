import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW


@wrap_template
def template(train=False, description=""):
    link = chainer.links.BatchNormalization(size=4)
    vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))

    if chainer.__version__ >= "2.":
        with chainer.using_config('train', train):
            vy = link(vx)
    else:
        vy = link(vx, test=not train)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] L.BatchNormalization {description}",
        graph=graph,
        inputs={x: np.transpose(vx.data, [OrderNCHW.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy.data, [OrderNCHW.axes_dict[a] for a in y.order.axes])}
    )


def test():
    template()
