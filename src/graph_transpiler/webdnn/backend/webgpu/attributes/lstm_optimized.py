from webdnn.graph.attribute import Attribute
from webdnn.graph.axis import Axis
from webdnn.graph.operators.lstm import LSTM


class LSTMOptimized(Attribute):
    def __init__(self, base: LSTM):
        self.base = base

        if "w_input" not in base.inputs:
            raise KeyError("[LSTMOptimized] 'w_input' is not found in inputs of LSTM operator."
                           "LSTMOptimized attribute must be attached before 'w_input' is removed")

        if "w_hidden" not in base.inputs:
            raise KeyError("[LSTMOptimized] 'w_hidden' is not found in inputs of LSTM operator."
                           "LSTMOptimized attribute must be attached before 'w_hidden' is removed")

        self.C1 = base.inputs["w_input"].shape_dict[Axis.C]
        self.C2 = base.inputs["w_hidden"].shape_dict[Axis.C]
