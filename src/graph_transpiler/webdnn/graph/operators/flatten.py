from typing import Optional, List

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.elementwise import Elementwise
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


# FIXME: improve documentation
class Flatten(Operator):
    """Flatten some axes into one axis.

    Args:
        name (str): Operator name.
        in_axes (set of :class:~`graph_transpiler.graph.Axis`): axes which are combined
        out_axes (set of :class:~`graph_transpiler.graph.Axis`): axes which `in_axes` are combined into  

    """

    # 入力変数の形を変形するレイヤー
    # データ内の特定の軸(複数)を特定の軸(現状、1つ)に射影
    # 入出力変数の形によっては、データそのものを転置する必要がある
    # NCHW -> NCなど

    def __init__(self, name: Optional[str], in_axes: List[Axis], out_axis: Axis):
        # in_axes: [Axis.H, Axis.W, Axis.C], out_axes: Axis.C
        # のとき、NHWC入力・NC出力ならデータを操作しないでorder=NCの出力とする。
        # NCHW入力・NC出力なら、入力データをNHWCに並び替えたうえでorder=NCの出力とする。

        super().__init__(name)

        self.parameters["in_axes"] = in_axes
        self.parameters["out_axis"] = out_axis
        self.attributes = {Elementwise(self),
                           Inplace(self, "x", "y")}

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        out_axes = list(x.order.axes)
        for axis in self.parameters["in_axes"]:
            if axis not in out_axes:
                raise ValueError(f"Axis {axis} is not contained in input variable")

            out_axes.remove(axis)

        out_shape = [x.shape_dict[axis] for axis in out_axes]

        if self.parameters["out_axis"] in out_axes:
            raise ValueError(f"Axis {axis} is duplicated")

        out_axes.append(self.parameters["out_axis"])
        out_shape.append(np.product([x.shape_dict[axis] for axis in self.parameters["in_axes"]]))

        y = Variable(out_shape, Order(out_axes))
        self.append_input("x", x)
        self.append_output("y", y)

        return y,
