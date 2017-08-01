import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW


@wrap_template
def template(r=2, description=""):
    vx = chainer.Variable(np.random.rand(2, 4, 6 * r, 8 * r).astype(np.float32))
    vy = chainer.functions.space2depth(vx, r)

    graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[chainer] F.Depth2Space {description}",
        graph=graph,
        backend=["webgpu", "webassembly"],
        inputs={x: np.transpose(vx.data, [OrderNCHW.axes_dict[a] for a in x.order.axes])},
        expected={y: np.transpose(vy.data, [OrderNCHW.axes_dict[a] for a in y.order.axes])},
    )


def test():
    template()


def test_r_3():
    template(r=3)
