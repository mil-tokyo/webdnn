from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.operators.compose import VariableAlias
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


class ConvScale(OptimizeRule):
    """
    conv + axiswise_scale をひとまとめにする
    """

    def __call__(self, graph: Operator):
        flag_changed = False

        for match in util.search_sub_structure(graph, [Convolution2D, AxiswiseScale]):
            conv: Convolution2D = match[0]
            axiswise_scale: AxiswiseScale = match[1]

            w = conv.inputs["w"]
            y1 = conv.outputs["y"]
            s = axiswise_scale.inputs["s"]
            y2 = axiswise_scale.outputs["y"]

            if isinstance(w, VariableAlias):
                w: ConstantVariable = w.original
            if isinstance(s, VariableAlias):
                s: ConstantVariable = s.original

            w.data *= s.data[None, None, :, None]
            axiswise_scale.remove_all()
            y1.merge(y2)
            flag_changed = True

        return graph, flag_changed
