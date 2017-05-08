from typing import Set

import numpy as np

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC


# FIXME: improve documentation
class Flatten(Operator):
    """Flatten some axes into one axis.

    Args:
        name (str): Operator name.
        in_axes (set of :class:~`graph_builder.graph.Axis`): axes which are combined
        out_axes (set of :class:~`graph_builder.graph.Axis`): axes which in_axes are combined into  

    """

    # 入力変数の形を変形するレイヤー
    # データ内の特定の軸(複数)を特定の軸(現状、1つ)に射影
    # 入出力変数の形によっては、データそのものを転置する必要がある
    # NCHW -> NCなど

    attributes = {PostElementwise,
                  PostAxiswise,
                  Inplace}

    def __init__(self, name: str, in_axes: Set[Axis], out_axes: Set[Axis]):
        # in_axes: [Axis.H, Axis.W, Axis.C], out_axes: [Axis.C]
        # のとき、NHWC入力・NC出力ならデータを操作しないでaxis_order=NCの出力とする。
        # NCHW入力・NC出力なら、入力データをNHWCに並び替えたうえでaxis_order=NCの出力とする。

        super().__init__(name)

        # FIXME: 現状はこの組み合わせだけで十分

        assert in_axes == {Axis.C, Axis.H, Axis.W}
        assert out_axes == {Axis.C}

        self.parameters["in_axes"] = in_axes
        self.parameters["out_axes"] = out_axes

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        out_axis_order = OrderNC  # FIXME: 決め打ちをしない

        reduction_size = int(np.prod([x.shape_dict[axis] for axis in self.parameters["in_axes"]]))
        keep_size = x.shape_dict[Axis.N]
        y = Variable((keep_size, reduction_size), out_axis_order)
        self.append_input("x", x)
        self.append_output("y", y)

        return y,
