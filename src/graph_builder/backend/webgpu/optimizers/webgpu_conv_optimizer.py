from graph_builder.backend.webgpu.optimize_rules.adjust_conv_weight_data_order import AdjustConvWeightDataOrder
from graph_builder.backend.webgpu.optimize_rules.conv_scale import ConvScale
from graph_builder.backend.webgpu.optimize_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from graph_builder.backend.webgpu.optimize_rules.sgemm_bias_relu import SgemmBiasRelu
from graph_builder.optimizer.optimizer import Optimizer


class WebGPUConvOptimizer(Optimizer):
    def __init__(self):
        super(WebGPUConvOptimizer, self).__init__()

        self.register(ConvScale())
        self.register(ReplaceConvolutionByIm2Col())
        self.register(AdjustConvWeightDataOrder())
        self.register(SgemmBiasRelu())
