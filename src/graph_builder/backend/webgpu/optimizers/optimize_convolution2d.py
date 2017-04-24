from graph_builder.backend.webgpu.optimize_rules.conv_scale import ConvScale
from graph_builder.backend.webgpu.optimize_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from graph_builder.optimizer.optimizer import Optimizer


class OptimizeConvolution2D(Optimizer):
    def __init__(self):
        super(OptimizeConvolution2D, self).__init__()

        self.register(ConvScale())
        self.register(ReplaceConvolutionByIm2Col())
