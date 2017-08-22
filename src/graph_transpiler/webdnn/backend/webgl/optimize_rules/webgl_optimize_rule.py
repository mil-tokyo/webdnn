from webdnn.backend.webgl.optimize_rules.optimize_channel_mode import OptimizeChannelMode
from webdnn.backend.webgl.optimize_rules.optimize_convolution2d import OptimizeConvolution2D
from webdnn.backend.webgl.optimize_rules.optimize_linear import OptimizeLinear
from webdnn.backend.webgl.optimize_rules.optimize_transpose import OptimizeTranspose
from webdnn.graph.graph import Graph
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.optimize_rule import OptimizeRule


class RemoveLastSoftmax(OptimizeRule):
    def optimize(self, graph: Graph):
        flag_changed = False
        for v in graph.outputs:
            op = v.output_from
            if not isinstance(op, Softmax):
                continue

            x = op.inputs["x"]
            y = op.outputs["y"]
            if y.order != x.order:
                x.change_order(y.order)

            op.remove_all()
            index = graph.outputs.index(y)
            graph.outputs.remove(y)
            graph.outputs.insert(index, x)
            flag_changed = True

        return graph, flag_changed


class WebGLOptimizeRule(OptimizeRule):
    def __init__(self):
        super(WebGLOptimizeRule, self).__init__()

        self.register(OptimizeTranspose())
        self.register(OptimizeConvolution2D())
        self.register(OptimizeLinear())
        self.register(OptimizeChannelMode())
        self.register(RemoveLastSoftmax())
