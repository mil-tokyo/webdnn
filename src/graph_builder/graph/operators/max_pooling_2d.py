from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import attributes as VA


class MaxPooling2D(Operator):
    """
    Max pooling (2D) レイヤー
    padding挙動はchainer準拠 (cover_allに注意)
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        """
        assert "ksize" in parameters
        assert "stride" in parameters
        assert "padding" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        x_shape_dict = x.shape_dict
        N = x_shape_dict[A.Axis.N]
        H2 = (x_shape_dict[A.Axis.H] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) // self.parameters["stride"][0] + 1
        W2 = (x_shape_dict[A.Axis.W] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) // self.parameters["stride"][1] + 1
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
