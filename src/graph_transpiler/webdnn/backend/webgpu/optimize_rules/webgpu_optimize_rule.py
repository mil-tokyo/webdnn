from typing import List

from webdnn.backend.webgpu.optimize_rules.concat_lstm_input_and_hidden import ConcatLSTMInputAndHidden
from webdnn.backend.webgpu.optimize_rules.insert_transpose import InsertTranspose
from webdnn.graph.optimize_rule import OptimizeRuleGroup, OptimizeRule
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.optimizer.sub_rules.dump_graph import DumpGraph
from webdnn.optimizer.sub_rules.elementwise_kernel_fusion import ElementwiseKernelFusion
from webdnn.optimizer.sub_rules.merge_tensordot_and_elementwise_mul import MergeTensordotAndElementwiseMul
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.remove_redundant_operator import RemoveRedundantOperator
from webdnn.optimizer.sub_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from webdnn.optimizer.sub_rules.replace_deconvolution_by_col2im import ReplaceDeconvolutionByCol2Im
from webdnn.optimizer.sub_rules.replace_linear_by_tensordot import ReplaceLinearByTensordot
from webdnn.optimizer.sub_rules.update_inplace_attribute import UpdateInplaceAttribute
from webdnn.util import flags


class WebGPUOptimizeRule(OptimizeRuleGroup):
    def __init__(self):
        sub_rules = [
            OptimizeRuleGroup([
                InsertTranspose(),
                ReplaceConvolutionByIm2Col(),
                ReplaceDeconvolutionByCol2Im(),
                ReplaceLinearByTensordot(),
                MergeTensordotAndElementwiseMul(),
                ConstantFolding(),
                ConcatLSTMInputAndHidden(),
                RemoveRedundantOperator(),
                RemoveNoEffectOperator(),
                UpdateInplaceAttribute()
            ]),
            ElementwiseKernelFusion()
        ]  # type: List[OptimizeRule]

        if flags.DEBUG:
            sub_rules.append(DumpGraph("cg{count}.dot"))

        super(WebGPUOptimizeRule, self).__init__(sub_rules)
