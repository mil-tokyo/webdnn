from webdnn.backend.webgpu.optimize_rules.concat_lstm_input_and_hidden import ConcatLSTMInputAndHidden
from webdnn.backend.webgpu.optimize_rules.insert_transpose import InsertTranspose
from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.optimizer.sub_rules.elementwise_kernel_fusion import ElementwiseKernelFusion
from webdnn.optimizer.sub_rules.merge_sgemm_and_elementwise_mul import MergeSgemmAndElementwiseMul
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.remove_redundant_operator import RemoveRedundantOperator
from webdnn.optimizer.sub_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from webdnn.optimizer.sub_rules.replace_deconvolution_by_col2im import ReplaceDeconvolutionByCol2Im
from webdnn.optimizer.sub_rules.replace_linear_by_sgemm import ReplaceLinearBySgemm
from webdnn.optimizer.sub_rules.update_inplace_attribute import UpdateInplaceAttribute


class WebGPUOptimizeRule(OptimizeRuleGroup):
    def __init__(self):
        super(WebGPUOptimizeRule, self).__init__([
            OptimizeRuleGroup([
                InsertTranspose(),
                ReplaceConvolutionByIm2Col(),
                MergeSgemmAndElementwiseMul(),
                ConstantFolding(),
                ReplaceDeconvolutionByCol2Im(),
                MergeSgemmAndElementwiseMul(),
                ConstantFolding(),
                ReplaceLinearBySgemm(),
                MergeSgemmAndElementwiseMul(),
                ConstantFolding(),
                ConcatLSTMInputAndHidden(),
                RemoveRedundantOperator(),
                RemoveNoEffectOperator(),
                UpdateInplaceAttribute()
            ]),
            ElementwiseKernelFusion()
        ])
