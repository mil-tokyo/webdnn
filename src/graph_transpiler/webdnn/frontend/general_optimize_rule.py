from webdnn.frontend.sub_rules.concat_affine import ConcatAffine
from webdnn.frontend.sub_rules.concat_scalar_affine import ConcatScalarAffine
from webdnn.frontend.sub_rules.remove_last_softmax import RemoveLastSoftmax
from webdnn.frontend.sub_rules.concat_zero_padding import ConcatZeroPadding
from webdnn.graph.optimize_rule import OptimizeRule


class GeneralOptimizeRule(OptimizeRule):
    def __init__(self):
        super(GeneralOptimizeRule, self).__init__()

        self.register(RemoveLastSoftmax())
        self.register(ConcatAffine())
        self.register(ConcatScalarAffine())
        self.register(ConcatZeroPadding())
