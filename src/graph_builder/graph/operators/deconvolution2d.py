from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class Deconvolution2D(Operator):
    """
    Deconvolutionレイヤー(bias含まず)
    """
    attributes = {A.PostElementwise,
                  A.PostChannelwise,
                  A.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object] = None):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "ksize" in parameters
        assert "stride" in parameters
        assert "padding" in parameters
        assert "in_size" in parameters
        assert "out_size" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        N = x.shape[0]
        H2 = (x.shape[1] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) / self.parameters["stride"][0] + 1
        W2 = (x.shape[2] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) / self.parameters["stride"][1] + 1
        C2 = self.parameters["out_size"]

        y = Variable([N, H2, W2, C2])
        self.append_input("x", x)
        self.append_input("w", w)
        self.append_output("y", y)
        return y,
