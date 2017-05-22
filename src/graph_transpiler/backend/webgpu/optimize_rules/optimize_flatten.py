from graph_transpiler.backend.webgpu.optimize_rules.sub_rules.remove_unnecessary_flatten import RemoveUnnecessaryFlatten
from graph_transpiler.graph.optimize_rule import OptimizeRule


class OptimizeFlatten(OptimizeRule):
    def __init__(self):
        super(OptimizeFlatten, self).__init__()
        self.register(RemoveUnnecessaryFlatten())
