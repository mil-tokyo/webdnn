from graph_builder.backend.webgpu.optimize_rules.conv_scale import ConvScale
from graph_builder.backend.webgpu.optimize_rules.replace_deconvolution_by_col2im import ReplaceDeconvolutionByCol2Im
from graph_builder.optimizer.optimizer import Optimizer


class OptimizeDeconvolution2D(Optimizer):
    def __init__(self):
        super(OptimizeDeconvolution2D, self).__init__()

        self.register(ConvScale())
        self.register(ReplaceDeconvolutionByCol2Im())
