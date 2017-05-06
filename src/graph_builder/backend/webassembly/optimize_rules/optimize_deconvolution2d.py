from graph_builder.backend.webassembly.optimize_rules.sub_rules.replace_deconvolution_by_col2im import ReplaceDeconvolutionByCol2Im
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class OptimizeDeconvolution2D(OptimizeRule):
    def __init__(self):
        super(OptimizeDeconvolution2D, self).__init__()

        self.register(ReplaceDeconvolutionByCol2Im())
