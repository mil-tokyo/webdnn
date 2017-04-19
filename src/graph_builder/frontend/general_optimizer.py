from graph_builder.frontend.optimize_rules.concat_axiswise_operation import ConcatAxiswiseOperation
from graph_builder.frontend.optimize_rules.concat_elementwise_operation import ConcatElementwiseOperation
from graph_builder.optimizer import Optimizer


class GeneralOptimizer(Optimizer):
    def __init__(self):
        super(GeneralOptimizer, self).__init__()

        self.register_rule(ConcatAxiswiseOperation())
        self.register_rule(ConcatElementwiseOperation())
