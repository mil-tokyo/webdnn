from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator


class TensorFlowFrontendOptimizeRule(OptimizeRuleGroup):
    def __init__(self):
        super(TensorFlowFrontendOptimizeRule, self).__init__([
            RemoveNoEffectOperator()
        ])
