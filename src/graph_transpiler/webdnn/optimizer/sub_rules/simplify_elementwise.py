from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.replace_scalar_operator import ReplaceScalarOperator
from webdnn.optimizer.sub_rules.simplify_associative_operator import SimplifyAssociativeOperator
from webdnn.optimizer.sub_rules.simplify_commutative_operator import SimplifyCommutativeOperator
from webdnn.optimizer.sub_rules.simplify_elementwise_sequential import SimplifyElementwiseSequential
from webdnn.optimizer.sub_rules.simplify_split_axis import SimplifySplitAxis
from webdnn.util import flags


class SimplifyElementwise(OptimizeRuleGroup):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE
        ]

    def __init__(self):
        super(SimplifyElementwise, self).__init__([
            RemoveNoEffectOperator(),
            ReplaceScalarOperator(),
            SimplifyElementwiseSequential(),
            SimplifySplitAxis(),
            SimplifyCommutativeOperator(),
            SimplifyAssociativeOperator()
        ])
