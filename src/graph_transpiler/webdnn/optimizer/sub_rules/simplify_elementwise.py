from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.replace_scalar_affine import ReplaceScalarAffine
from webdnn.optimizer.sub_rules.simplify_elementwise_parallel import SimplifyElementwiseParallel
from webdnn.optimizer.sub_rules.simplify_elementwise_sequential import SimplifyElementwiseSequential
from webdnn.util import flags


class SimplifyElementwise(OptimizeRule):
    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_ELEMENTWISE
        ]

    def __init__(self):
        super(SimplifyElementwise, self).__init__()

        self.register(RemoveNoEffectOperator())
        self.register(ReplaceScalarAffine())
        self.register(SimplifyElementwiseSequential())
        self.register(SimplifyElementwiseParallel())
