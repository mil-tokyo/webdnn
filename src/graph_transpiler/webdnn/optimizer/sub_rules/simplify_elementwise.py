from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.replace_scalar_operator import ReplaceScalarOperator
from webdnn.optimizer.sub_rules.simplify_associative_operator import SimplifyAssociativeOperatorLeftHand, \
    SimplifyAssociativeOperatorRightHand
from webdnn.optimizer.sub_rules.simplify_commutative_operator import SimplifyCommutativeOperator
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
        self.register(ReplaceScalarOperator())
        self.register(SimplifyElementwiseSequential())
        self.register(SimplifyCommutativeOperator())
        self.register(SimplifyAssociativeOperatorRightHand())
        self.register(ConstantFolding())
        self.register(SimplifyAssociativeOperatorLeftHand())
        self.register(ConstantFolding())
