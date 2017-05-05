from graph_builder.backend.webassembly.optimize_rules.optimize_affine_transform import OptimizeAffineTransform
from graph_builder.backend.webassembly.optimize_rules.optimize_convolution2d import OptimizeConvolution2D
from graph_builder.backend.webassembly.optimize_rules.optimize_deconvolution2d import OptimizeDeconvolution2D
from graph_builder.backend.webassembly.optimize_rules.optimize_elementwise import OptimizeElementwise
from graph_builder.backend.webassembly.optimize_rules.optimize_sgemm_eigen import OptimizeSgemmEigen
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class WebassemblyOptimizeRule(OptimizeRule):
    def __init__(self):
        super(WebassemblyOptimizeRule, self).__init__()

        self.register(OptimizeConvolution2D())
        self.register(OptimizeDeconvolution2D())
        self.register(OptimizeAffineTransform())
        self.register(OptimizeElementwise())
        self.register(OptimizeSgemmEigen())
