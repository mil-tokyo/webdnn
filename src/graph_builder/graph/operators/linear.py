from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class Linear(Operator):
    """
    行列積レイヤー(bias含まず)
    Convolutionの後に接続する場合、Reshapeレイヤーで2次元入力(n, c)に変換してから入力する
    """
    attributes = {A.PostElementwise,
                  A.PostChannelwise,
                  A.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object] = None):
        """
        weights["W"]: (in_size, out_size)
        :param name: 
        :param parameters: 
        """
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        self.append_input("x", x)
        self.append_input("w", w)
        y = Variable([x.shape[0], w.shape[1]])
        self.append_output("y", y)
        return y,
