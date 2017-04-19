from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class AveragePooling2D(Operator):
    """
    Average pooling (2D) レイヤー
    padding挙動はchainer準拠
    当面はglobal average poolingだけ実装
    """
    attributes = {A.PostElementwise,
                  A.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "out_size" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        N = x.shape[0]
        H2 = (x.shape[1] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) / self.parameters["stride"][0] + 1
        W2 = (x.shape[2] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) / self.parameters["stride"][1] + 1
        C2 = self.parameters["out_size"]

        y = Variable([N, H2, W2, C2])
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
