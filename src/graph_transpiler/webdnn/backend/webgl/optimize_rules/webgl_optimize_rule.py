from webdnn.backend.webgl.optimize_rules.optimize_convolution2d import OptimizeConvolution2D
from webdnn.backend.webgl.optimize_rules.optimize_linear import OptimizeLinear
from webdnn.backend.webgl.optimize_rules.optimize_transpose import OptimizeTranspose
from webdnn.graph.optimize_rule import OptimizeRule


class WebGLOptimizeRule(OptimizeRule):
    def __init__(self):
        super(WebGLOptimizeRule, self).__init__()

        self.register(OptimizeTranspose())
        self.register(OptimizeConvolution2D())
        self.register(OptimizeLinear())
