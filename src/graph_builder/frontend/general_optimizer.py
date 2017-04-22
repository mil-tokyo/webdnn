from graph_builder.frontend.optimize_rules.affine_concat import AffineConcat
from graph_builder.frontend.optimize_rules.remove_last_softmax import RemoveLastSoftmax
from graph_builder.optimizer.optimizer import Optimizer


class GeneralOptimizer(Optimizer):
    def __init__(self):
        super(GeneralOptimizer, self).__init__()

        # self.register(ComposeAxiswiseOperation())
        # self.register(ComposeElementwiseOperation())
        self.register(RemoveLastSoftmax())
        self.register(AffineConcat())
