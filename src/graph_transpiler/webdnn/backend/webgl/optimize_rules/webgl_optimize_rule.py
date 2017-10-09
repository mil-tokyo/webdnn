from webdnn.backend.webgl.optimize_rules.attach_concat_workspace import AttachConcatWorkspace
from webdnn.backend.webgl.optimize_rules.decompose_softmax import DecomposeSoftmax
from webdnn.backend.webgl.optimize_rules.fix_sgemm_texture_shape import FixSGEMMTextureShape
from webdnn.backend.webgl.optimize_rules.insert_channel_mode_conversion import InsertChannelModeConversion
from webdnn.backend.webgl.optimize_rules.insert_transpose import InsertTranspose
from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_channel_mode_conversion import \
    SimplifyChannelModeConversion
from webdnn.backend.webgl.optimize_rules.split_texture.split_texture import SplitTexture
from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.optimizer.sub_rules.merge_sgemm_and_elementwise_mul import MergeSgemmAndElementwiseMul
from webdnn.optimizer.sub_rules.remove_redundant_operator import RemoveRedundantOperator
from webdnn.optimizer.sub_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from webdnn.optimizer.sub_rules.replace_deconvolution_by_col2im import ReplaceDeconvolutionByCol2Im
from webdnn.optimizer.sub_rules.replace_linear_by_sgemm import ReplaceLinearBySgemm
from webdnn.optimizer.sub_rules.simplify_elementwise import SimplifyElementwise


class WebGLOptimizeRule(OptimizeRuleGroup):
    def __init__(self):
        super(WebGLOptimizeRule, self).__init__([
            OptimizeRuleGroup([
                InsertTranspose(),
                ReplaceConvolutionByIm2Col(),
                ReplaceDeconvolutionByCol2Im(),
                DecomposeSoftmax(),
                ReplaceLinearBySgemm(),
                MergeSgemmAndElementwiseMul(),
                FixSGEMMTextureShape(optimize_channel_mode=False),
                ConstantFolding(),
                SplitTexture(),
            ]),
            OptimizeRuleGroup([
                InsertChannelModeConversion(),
                SimplifyElementwise(),
                RemoveRedundantOperator(),
                SimplifyChannelModeConversion(),
                FixSGEMMTextureShape(optimize_channel_mode=True),
            ]),
            AttachConcatWorkspace(),
        ], repeat=False)
