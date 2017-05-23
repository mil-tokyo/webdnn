from webdnn.backend.webgpu.optimize_rules.optimize_convolution2d import OptimizeConvolution2D
from webdnn.backend.webgpu.optimize_rules.optimize_deconvolution2d import OptimizeDeconvolution2D
from webdnn.backend.webgpu.optimize_rules.optimize_flatten import OptimizeFlatten
from webdnn.backend.webgpu.optimize_rules.optimize_inline_inplace import OptimizeInlineInplace
from webdnn.backend.webgpu.optimize_rules.optimize_linear import OptimizeLinear
from webdnn.graph.optimize_rule import OptimizeRule


class WebGPUOptimizeRule(OptimizeRule):
    def __init__(self):
        super(WebGPUOptimizeRule, self).__init__()

        self.register(OptimizeConvolution2D())
        self.register(OptimizeDeconvolution2D())
        self.register(OptimizeInlineInplace())
        self.register(OptimizeFlatten())
        self.register(OptimizeLinear())
