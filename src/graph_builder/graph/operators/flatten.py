from typing import Dict, List
import numpy as np

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


class Flatten(Operator):
    """
    入力変数の形を変形するレイヤー
    データ内の特定の軸(複数)を特定の軸(現状、1つ)に射影
    入出力変数の形によっては、データそのものを転置する必要がある
    NCHW -> NCなど
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise,
                  A.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {in_axes: List[A.Axis], out_axes: List[A.Axis]}
        in_axes: [A.Axis.H, A.Axis.W, A.Axis.C], out_axes: [A.Axis.C]
        のとき、NHWC入力・NC出力ならデータを操作しないでaxis_order=NCの出力とする。
        NCHW入力・NC出力なら、入力データをNHWCに並び替えたうえでaxis_order=NCの出力とする。
        :param name: 
        :param parameters: 
        """
        assert "in_axes" in parameters
        assert "out_axes" in parameters
        # 現状この組み合わせだけで十分
        assert set(parameters["in_axes"]) == {A.Axis.C, A.Axis.H, A.Axis.W}
        assert set(parameters["out_axes"]) == {A.Axis.C}

        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        out_axis_order = VA.OrderNC
        reduction_size = int(np.prod([x.shape_dict[axis] for axis in self.parameters["in_axes"]]))
        keep_size = x.shape_dict[A.Axis.N]
        y = Variable((keep_size, reduction_size), out_axis_order)
        self.append_input("x", x)
        self.append_output("y", y)
        # ここでは別変数が返るので、データに変更がない場合でもコピーまたは同領域割り当てで最適化が必要
        return y,
