from graph_transpiler.backend.webgpu.optimize_rules.sub_rules.replace_linear_by_sgemm import ReplaceLinearBySgemm
from graph_transpiler.graph.optimize_rule import OptimizeRule


class OptimizeLinear(OptimizeRule):
    def __init__(self):
        super(OptimizeLinear, self).__init__()
        self.register(ReplaceLinearBySgemm())
