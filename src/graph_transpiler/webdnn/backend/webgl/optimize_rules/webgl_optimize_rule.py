from typing import List

from webdnn.backend.webgl.optimize_rules.decompose_softmax import DecomposeSoftmax
from webdnn.backend.webgl.optimize_rules.fix_tensordot_texture_shape import FixTensordotTextureShape
from webdnn.backend.webgl.optimize_rules.insert_channel_mode_conversion import InsertChannelModeConversion
from webdnn.backend.webgl.optimize_rules.insert_transpose import InsertTranspose
from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_channel_mode_conversion import \
    SimplifyChannelModeConversion
from webdnn.backend.webgl.optimize_rules.split_texture.split_texture import SplitTexture
from webdnn.backend.webgl.optimize_rules.unroll_concat import UnrollConcat
from webdnn.graph.optimize_rule import OptimizeRuleGroup, OptimizeRule
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.optimizer.sub_rules.dump_graph import DumpGraph
from webdnn.optimizer.sub_rules.merge_tensordot_and_elementwise_mul import MergeTensordotAndElementwiseMul
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.remove_redundant_operator import RemoveRedundantOperator
from webdnn.optimizer.sub_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from webdnn.optimizer.sub_rules.replace_deconvolution_by_col2im import ReplaceDeconvolutionByCol2Im
from webdnn.optimizer.sub_rules.replace_linear_by_tensordot import ReplaceLinearByTensordot
from webdnn.util import flags, config


class WebGLOptimizeRule(OptimizeRuleGroup):
    def __init__(self):
        sub_rules = [
            OptimizeRuleGroup([
                InsertTranspose(),
                ReplaceConvolutionByIm2Col(),
                ReplaceDeconvolutionByCol2Im(),
                ReplaceLinearByTensordot(),
                DecomposeSoftmax(),
                FixTensordotTextureShape(),
                MergeTensordotAndElementwiseMul(),
                ConstantFolding(),
                RemoveRedundantOperator(),
                RemoveNoEffectOperator(),
                SplitTexture(),
                UnrollConcat(),
            ]),
            OptimizeRuleGroup([
                InsertTranspose(),
                InsertChannelModeConversion(),
                SimplifyChannelModeConversion(),
                ConstantFolding(),
                RemoveRedundantOperator(),
                RemoveNoEffectOperator(),
            ]),
        ]  # type: List[OptimizeRule]

        if flags.DEBUG:
            sub_rules.append(DumpGraph(f"cg_{config.WEBGL_MAX_TEXTURE_SIZE}_{{count}}.dot"))

        super(WebGLOptimizeRule, self).__init__(sub_rules, repeat=False)
