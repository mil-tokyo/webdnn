from typing import Dict, List

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class Concat(Operator):
    """
    n入力を連結するレイヤー
    結合軸はparametersで指定(chainerと同じ挙動)
    """
    attributes = {A.PostElementwise,
                  A.PostAxiswise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {axis: int}
        :param name: 
        :param parameters: 
        """
        assert "axis" in parameters
        assert isinstance(parameters["axis"], A.Axis)
        super().__init__(name, parameters)

    def __call__(self, *xs: Variable):
        axis = self.parameters["axis"]  # type: int
        axis_index = xs[0].axis_order.axes_dict[axis]

        y_shape = list(xs[0].shape)  # type: List[int]
        y_shape[axis_index] = 0

        for i, x in enumerate(xs):
            self.append_input(f"x{i}", x)
            y_shape[axis_index] += x.shape_dict[axis]

        y = Variable(y_shape, xs[0].axis_order)
        self.append_output("y", y)
        return y,
