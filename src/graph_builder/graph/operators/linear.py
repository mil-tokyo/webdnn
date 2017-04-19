from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


class Linear(Operator):
    """
    行列積レイヤー(bias含まず)
    入力は2次元または4次元, C or CHW方向に内積を取り、wのNが出力次元
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise,
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

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict
        assert x_shape_dict["C"] == w_shape_dict["C"]
        assert len(x_shape_dict) == len(w_shape_dict)
        if len(x_shape_dict) == 4:
            assert x_shape_dict["H"] == w_shape_dict["H"]
            assert x_shape_dict["W"] == w_shape_dict["W"]
        y = Variable([x_shape_dict["N"], w_shape_dict["N"]], VA.OrderNC)
        self.append_output("y", y)
        return y,
