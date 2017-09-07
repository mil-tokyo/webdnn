from webdnn.backend.webgpu.optimize_rules.optimize_convolution2d import OptimizeConvolution2D
from webdnn.backend.webgpu.optimize_rules.optimize_deconvolution2d import OptimizeDeconvolution2D
from webdnn.backend.webgpu.optimize_rules.optimize_linear import OptimizeLinear
from webdnn.backend.webgpu.optimize_rules.optimize_lstm import OptimizeLSTM
from webdnn.backend.webgpu.optimize_rules.optimize_transpose import OptimizeTranspose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.optimizer.sub_rules.elementwise_kernel_fusion import ElementwiseKernelFusion
from webdnn.optimizer.sub_rules.remove_no_effect_operator import RemoveNoEffectOperator
from webdnn.optimizer.sub_rules.remove_redundant_operator import RemoveRedundantOperator


class WebGPUOptimizeRule(OptimizeRule):
    def __init__(self):
        super(WebGPUOptimizeRule, self).__init__()

        self.register(OptimizeTranspose())
        self.register(OptimizeConvolution2D())
        self.register(OptimizeDeconvolution2D())
        self.register(OptimizeLinear())
        self.register(OptimizeLSTM())
        self.register(RemoveRedundantOperator())
        self.register(RemoveNoEffectOperator())
        self.register(ElementwiseKernelFusion())
