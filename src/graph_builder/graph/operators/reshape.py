from typing import Dict, List

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


class Reshape(Operator):
    """
    入力変数の形を変形するレイヤー
    形状変化を表現する便宜上のもので、データ操作はない
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise,
                  A.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {out_shape: Tuple, out_order: VA.Order}
        :param name: 
        :param parameters: 
        """
        assert "out_shape" in parameters
        assert "out_order" in parameters
        assert issubclass(type(parameters["out_order"]), VA.AxisOrder)
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        out_shape = self.parameters["out_shape"]  # type: List[int]
        y = Variable(out_shape, self.parameters["out_order"])
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
