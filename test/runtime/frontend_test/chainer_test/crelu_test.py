from unittest import SkipTest

import chainer
import numpy as np

from test.util import generate_kernel_test_case
from webdnn.frontend.chainer.converter import ChainerConverter
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNCHW, OrderNHWC
from webdnn.graph.variables.constant_variable import ConstantVariable

condition_default = {
    "x_order": OrderNHWC,
    "y_order": OrderNHWC,
    "axis": Axis.C,
    "backend": ["webgpu", "webassembly", "fallback"]
}


def test_general():
    for condition_custom in [
        {},
        {"x_order": OrderNCHW}
    ]:
        condition = dict(condition_default)
        condition.update(condition_custom)

        vx = chainer.Variable(np.random.rand(2, 4, 6, 8))
        vy = chainer.functions.crelu(vx, condition["x_order"].axes_dict[condition["axis"]])

        graph = ChainerConverter().convert_from_inout_vars([vx], [vy])

        x = graph.inputs[0]
        y = graph.outputs[0]

        x.change_order(condition["x_order"])
        y.change_order(condition["y_order"])

        generate_kernel_test_case(
            description=f"[chainer] F.crelu" + (", ".join([f"{k}={v}" for k, v in condition_custom.items()])),
            graph=graph,
            inputs={x: ConstantVariable(vx.data, OrderNCHW).change_order(x.order).data},
            expected={y: ConstantVariable(vy.data, OrderNCHW).change_order(y.order).data},
            raise_skip=False
        )

    raise SkipTest
