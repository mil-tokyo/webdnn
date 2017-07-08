from unittest import SkipTest

import numpy as np

from test.util import generate_kernel_test_case
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNHWC, OrderNCHW, OrderHWCN
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable

condition_default = {
    "x1_order": OrderNHWC,
    "x2_order": OrderNHWC,
    "y_order": OrderNHWC,
    "backend": ["webgpu", "webassembly", "fallback"]
}


def test_general():
    for condition_custom in [
        {},
        {"x1_order": OrderNCHW, "x2_order": OrderHWCN}
    ]:
        condition = dict(condition_default)
        condition.update(condition_custom)

        vx1 = np.random.rand(2, 3, 4, 5)
        vx2 = np.random.rand(2, 3, 4, 5)
        vy = vx1 + vx2

        x1 = Variable(vx1.shape, order=OrderNHWC)
        x2 = Variable(vx2.shape, order=OrderNHWC)
        y = x1 + x2

        x1.change_order(condition["x1_order"])
        x2.change_order(condition["x2_order"])
        y.change_order(condition["y_order"])

        generate_kernel_test_case(
            description=f"ElementwiseAdd: " + (", ".join([f"{k}={v}" for k, v in condition_custom.items()])),
            backend=condition["backend"],
            graph=Graph([x1, x2], [y]),
            inputs={
                x1: ConstantVariable(vx1, OrderNHWC).change_order(x1.order).data,
                x2: ConstantVariable(vx2, OrderNHWC).change_order(x2.order).data
            },
            expected={y: ConstantVariable(vy, OrderNHWC).change_order(y.order).data},
            raise_skip=False
        )

    raise SkipTest
