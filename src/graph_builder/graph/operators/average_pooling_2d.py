from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


class AveragePooling2D(Operator):
    """
    Average pooling (2D) レイヤー
    padding挙動はchainer準拠
    当面はglobal average poolingだけ実装
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        x_shape_dict = x.shape_dict
        N = x_shape_dict[A.Axis.N]
        H2 = (x_shape_dict[A.Axis.H] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) / self.parameters["stride"][0] + 1
        W2 = (x_shape_dict[A.Axis.W] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) / self.parameters["stride"][1] + 1
        C2 = x_shape_dict[A.Axis.C]

        if x.axis_order == VA.OrderNCHW:
            var_shape = [N, C2, H2, W2]
        elif x.axis_order == VA.OrderNHWC:
            var_shape = [N, H2, W2, C2]
        else:
            raise NotImplementedError()
        y = Variable(var_shape, x.axis_order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
