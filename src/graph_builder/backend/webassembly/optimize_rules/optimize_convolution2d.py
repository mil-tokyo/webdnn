from graph_builder.backend.webassembly.optimize_rules.sub_rules.conv_scale import ConvScale
from graph_builder.backend.webassembly.optimize_rules.sub_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class OptimizeConvolution2D(OptimizeRule):
    def __init__(self):
        super(OptimizeConvolution2D, self).__init__()

        self.register(ConvScale())
        self.register(ReplaceConvolutionByIm2Col())
