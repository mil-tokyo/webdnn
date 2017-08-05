from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator


class TensorFlowFrontendOptimizeRule(OptimizeRule):
    def __init__(self):
        super(TensorFlowFrontendOptimizeRule, self).__init__()

        self.register(RemoveNoEffectOperator())
