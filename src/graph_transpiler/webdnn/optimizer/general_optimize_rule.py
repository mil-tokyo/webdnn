from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.optimizer.sub_rules.concat_affine import ConcatAffine
from webdnn.optimizer.sub_rules.concat_scalar_operation import ConcatScalarOperation
from webdnn.optimizer.sub_rules.concat_zero_padding import ConcatZeroPadding
from webdnn.optimizer.sub_rules.remove_last_softmax import RemoveLastSoftmax
from webdnn.optimizer.sub_rules.remove_unnecessary_operator import RemoveUnnecessaryOperator


class GeneralOptimizeRule(OptimizeRule):
    def __init__(self):
        super(GeneralOptimizeRule, self).__init__()

        self.register(RemoveLastSoftmax())
        self.register(ConcatAffine())
        self.register(ConcatScalarOperation())
        self.register(RemoveUnnecessaryOperator())
        self.register(ConcatZeroPadding())
