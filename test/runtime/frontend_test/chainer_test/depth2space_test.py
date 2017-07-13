from unittest import SkipTest

import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.order import OrderNCHW, OrderNHWC
from webdnn.graph.variables.constant_variable import ConstantVariable


def test():
    condition_default = {
        "x_order": OrderNHWC,
        "y_order": OrderNHWC,
        "backend": ["webgpu", "webassembly"],
        "r": 2
    }

    for condition_custom in [
        {},
        {"r": 1},
    ]:
        condition = dict(condition_default)
        condition.update(condition_custom)
        r = condition["r"]

        vx = chainer.Variable(np.random.rand(2, 4, 6, 8).astype(np.float32))
        vy = chainer.functions.depth2space(vx, r)

        graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

        x = graph.inputs[0]
        y = graph.outputs[0]

        generate_kernel_test_case(
            description=f"[chainer] F.Depth2Space",
            graph=graph,
            backend=["webgpu", "webassembly"],
            inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
            expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data},
            raise_skip=False
        )

    raise SkipTest
