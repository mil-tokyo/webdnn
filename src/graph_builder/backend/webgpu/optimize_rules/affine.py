from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.constant_bias import ConstantBias
from graph_builder.graph.operators.constant_scale import ConstantScale
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


def _convert(op1: Operator, op2: Operator, scale: float, bias: float):
    x = op1.inputs["x"]
    y = op2.outputs["y"]

    op1.remove_all()
    op2.remove_all()

    op = Operator("affine")
    op.append_input("x", x)
    op.append_output("y", y)
    op.parameters["custom_kernel"] = affine
    op.parameters["scale"] = scale
    op.parameters["bias"] = bias


class Affine(OptimizeRule):
    """
    ConstantScale, ConstantBiasをひとまとめにしてAffineとする
    """

    # FIXME GeneralOptimizerのAffineConcatと紛らわしい

    def __call__(self, graph: Operator):
        flag_changed = False

        for match in util.search_sub_structure(graph, [ConstantScale, ConstantBias]):
            _convert(match[0], match[1],)
            scale: ConstantScale = match[0]
            bias: ConstantBias = match[1]

            x = scale.inputs["x"]
            y = bias.outputs["y"]

            scale.remove_all()
            bias.remove_all()

            op = Operator("affine")
            op.append_input("x", x)
            op.append_output("y", y)
            op.parameters["custom_kernel"] = affine
            op.parameters["scale"] = scale.parameters["value"]
            op.parameters["bias"] = scale.parameters["value"]

            flag_changed = True

        for match in util.search_sub_structure(graph, [ConstantBias, ConstantScale]):
            scale: ConstantScale = match[0]
            bias: ConstantBias = match[1]

            x = scale.inputs["x"]
            y = bias.outputs["y"]

            scale.remove_all()
            bias.remove_all()

            op = Operator("affine")
            op.append_input("x", x)
            op.append_output("y", y)
            op.parameters["custom_kernel"] = affine
            op.parameters["scale"] = scale.parameters["value"]
            op.parameters["bias"] = scale.parameters["value"]

            flag_changed = True

        return graph, flag_changed
