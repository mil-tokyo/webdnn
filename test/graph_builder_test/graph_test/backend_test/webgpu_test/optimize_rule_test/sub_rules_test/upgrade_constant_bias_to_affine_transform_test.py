from graph_builder.backend.webgpu.operators.affine_transform import AffineTransform
from graph_builder.backend.webgpu.optimize_rules.optimize_affine_transform import UpgradeConstantBiasToAffineTransform
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.constant_bias import ConstantBias
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.order import OrderNC
from graph_builder.optimize_rule.util import listup_operators


def test_single_bias():
    bias = ConstantBias("bias", {"value": 2})

    x = Variable([5, 5], OrderNC)
    y, = bias(x)

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = UpgradeConstantBiasToAffineTransform().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], AffineTransform)
    assert len(graph.inputs) == 1 and ops[0].inputs["x"] == graph.inputs[0]
    assert len(graph.outputs) == 1 and ops[0].outputs["y"] == graph.outputs[0]
    assert ops[0].parameters["bias"] == bias.parameters["value"]
    assert ops[0].parameters["scale"] == 1
