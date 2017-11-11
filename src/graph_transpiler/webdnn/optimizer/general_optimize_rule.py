from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.optimizer.sub_rules.concat_zero_padding import ConcatZeroPadding
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.optimizer.sub_rules.conv_filter_pruning import ConvFilterPruning
from webdnn.optimizer.sub_rules.convolution2d_svd_compression import Convolution2DSvdCompression
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.remove_redundant_operator import RemoveRedundantOperator
from webdnn.optimizer.sub_rules.replace_scalar_operator import ReplaceScalarOperator
from webdnn.optimizer.sub_rules.simplify_associative_operator import SimplifyAssociativeOperator
from webdnn.optimizer.sub_rules.simplify_elementwise_sequence import SimplifyElementwiseSequence
from webdnn.optimizer.sub_rules.simplify_split_axis import SimplifySplitAxis
from webdnn.optimizer.sub_rules.upgrade_operator_type import UpgradeOperatorType


class GeneralOptimizeRule(OptimizeRuleGroup):
    def __init__(self):
        super(GeneralOptimizeRule, self).__init__([
            RemoveRedundantOperator(),
            RemoveNoEffectOperator(),
            RemoveNoEffectOperator(),
            ReplaceScalarOperator(),
            SimplifyElementwiseSequence(),
            SimplifySplitAxis(),
            SimplifyAssociativeOperator(),
            ConcatZeroPadding(),
            ConstantFolding(),
            Convolution2DSvdCompression(),
            ConvFilterPruning(),
            UpgradeOperatorType()
        ])
