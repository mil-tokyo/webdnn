from graph_builder.frontend.sub_rules.concat_affine import ConcatAffine
from graph_builder.frontend.sub_rules.concat_scalar_affine import ConcatScalarAffine
from graph_builder.frontend.sub_rules.remove_last_softmax import RemoveLastSoftmax
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class GeneralOptimizeRule(OptimizeRule):
    def __init__(self):
        super(GeneralOptimizeRule, self).__init__()

        self.register(RemoveLastSoftmax())
        self.register(ConcatAffine())
        self.register(ConcatScalarAffine())
