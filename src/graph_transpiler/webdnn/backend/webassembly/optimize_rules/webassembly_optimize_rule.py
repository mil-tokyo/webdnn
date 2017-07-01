from webdnn.backend.webassembly.optimize_rules.optimize_convolution2d import OptimizeConvolution2D
from webdnn.backend.webassembly.optimize_rules.optimize_deconvolution2d import OptimizeDeconvolution2D
from webdnn.backend.webassembly.optimize_rules.optimize_linear import OptimizeLinear
from webdnn.backend.webassembly.optimize_rules.optimize_sgemm_eigen import OptimizeSgemmEigen
from webdnn.graph.optimize_rule import OptimizeRule


class WebassemblyOptimizeRule(OptimizeRule):
    def __init__(self):
        super(WebassemblyOptimizeRule, self).__init__()

        self.register(OptimizeConvolution2D())
        self.register(OptimizeDeconvolution2D())
        self.register(OptimizeLinear())
        self.register(OptimizeSgemmEigen())
