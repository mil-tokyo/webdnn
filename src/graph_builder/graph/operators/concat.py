from typing import Dict, List

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class Concat(Operator):
    """
    n入力を連結するレイヤー
    結合軸はparametersで指定(chainerと同じ挙動)
    """
    attributes = {A.PostElementwise,
                  A.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {axis: int, n_inputs: int}
        n_inputs: 入力変数の数
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "axis" in parameters
        super().__init__(name, parameters)

    def __call__(self, *xs: Variable):
        axis = self.parameters["axis"]  # type: int
        y_shape = list(xs[0].shape)  # type: List[int]
        y_shape[axis] = 0
        for i, x in enumerate(xs):
            self.append_input(f"x{i}", x)
            y_shape[axis] += x.shape[axis]

        y = Variable(y_shape)
        self.append_output("y", y)
        return y,
