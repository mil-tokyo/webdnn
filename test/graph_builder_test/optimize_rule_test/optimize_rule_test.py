from graph_builder.graph.operator import Operator
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class MyOptimizeRule1(OptimizeRule):
    def __init__(self):
        super().__init__()
        self.register(MyOptimizeRule2())


class MyOptimizeRule2(OptimizeRule):
    def optimize(self, graph: Operator):
        if "optimized" in graph.parameters:
            return graph, False

        graph.parameters["optimized"] = True
        return graph, True


class MyOptimizeRule3(OptimizeRule):
    pass


def test_register_sub_rule():
    rule = MyOptimizeRule1()
    assert len(rule.sub_rules) == 1


def test_run_sub_rule():
    rule = MyOptimizeRule1()
    graph, _ = rule.optimize(Operator("test"))
    assert graph.parameters["optimized"]


def test_empty_rule():
    rule = MyOptimizeRule3()
    graph1 = Operator("test")
    graph2, _ = rule.optimize(graph1)
    assert graph1 == graph2
