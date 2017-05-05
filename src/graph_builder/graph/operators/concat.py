from typing import Dict, List

from graph_builder.graph.axis import Axis
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


class Concat(Operator):
    """
    n入力を連結するレイヤー
    結合軸はparametersで指定(chainerと同じ挙動)
    """
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {axis: int}
        :param name: 
        :param parameters: 
        """
        assert "axis" in parameters
        assert isinstance(parameters["axis"], Axis)
        super().__init__(name, parameters)

    def __call__(self, *xs: Variable):
        axis = self.parameters["axis"]  # type: int
        axis_index = xs[0].axis_order.axes_dict[axis]

        y_shape = list(xs[0].shape)  # type: List[int]
        y_shape[axis_index] = 0

        for i, x in enumerate(xs):
            for other_axis in [other_axis for other_axis in Axis if other_axis != axis]:
                assert xs[0].shape_dict[other_axis] == x.shape_dict[other_axis]

            self.append_input(f"x{i}", x)
            y_shape[axis_index] += x.shape_dict[axis]

        y = Variable(y_shape, xs[0].axis_order)
        self.append_output("y", y)
        return y,
