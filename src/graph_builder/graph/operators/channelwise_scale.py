from typing import Dict

from graph_builder.graph.graph import Operator, Variable
from graph_builder.graph.operators import attributes as A


class ChannelwiseScale(Operator):
    """
    Channelwiseにウェイトを乗算するレイヤー
    """
    attributes = {A.PostElementwise,
                  A.PostChannelwise,
                  A.Channelwise,
                  A.Inplace,
                  A.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        super().__init__(name, parameters)

    def __call__(self, x: Variable, s: Variable):
        y = Variable(x.shape)
        self.append_input("x", x)
        self.append_input("s", s)
        self.append_output("y", y)
        return y,
