from typing import Dict, List

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class Reshape(Operator):
    """
    入力変数の形を変形するレイヤー
    形状変化を表現する便宜上のもので、データ操作はない
    """
    attributes = {A.PostElementwise,
                  A.PostChannelwise,
                  A.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object] = None):
        """
        parameters: {out_shape: Tuple}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "out_shape" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        out_shape = self.parameters["out_shape"]  # type: List[int]
        y = Variable(out_shape)
        self.append_input("x", x)
        self.append_output("y", y)
        return y
