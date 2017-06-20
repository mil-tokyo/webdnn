from webdnn.backend.webgpu.optimize_rules.sub_rules.concat_lstm_input_and_hidden import ConcatLSTMInputAndHidden
from webdnn.graph.optimize_rule import OptimizeRule


class OptimizeLSTM(OptimizeRule):
    def __init__(self):
        super(OptimizeLSTM, self).__init__()
        self.register(ConcatLSTMInputAndHidden())
