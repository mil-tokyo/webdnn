from typing import Dict

from graph_builder.graph.operator import Operator
from graph_builder.graph.axis import Axis
from graph_builder.graph.operators.attributes.have_weights import HaveWeights
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC


class Linear(Operator):
    """
    行列積レイヤー(bias含まず)
    入力は2次元または4次元, C or CHW方向に内積を取り、wのNが出力次元
    """
    attributes = {PostElementwise,
                  PostAxiswise,
                  HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object] = None):
        """
        :param name: 
        :param parameters: 
        """
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        self.append_input("x", x)
        self.append_input("w", w)

        x_shape_dict = x.shape_dict
        w_shape_dict = w.shape_dict
        assert x_shape_dict[Axis.C] == w_shape_dict[Axis.C]
        assert len(x_shape_dict) == len(w_shape_dict)
        if len(x_shape_dict) == 4:
            assert x_shape_dict[Axis.H] == w_shape_dict[Axis.H]
            assert x_shape_dict[Axis.W] == w_shape_dict[Axis.W]
        y = Variable([x_shape_dict[Axis.N], w_shape_dict[Axis.N]], OrderNC)
        self.append_output("y", y)
        return y,
