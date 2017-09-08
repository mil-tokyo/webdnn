from webdnn.backend.webgl.optimize_rules.fix_sgemm_texture_shape import FixSGEMMTextureShape
from webdnn.backend.webgl.optimize_rules.insert_transpose import InsertTranspose
from webdnn.backend.webgl.optimize_rules.replace_convolution_by_im2col import ReplaceConvolutionByIm2Col
from webdnn.backend.webgl.optimize_rules.replace_linear_by_sgemm import ReplaceLinearBySGEMM
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

        self.register(InsertTranspose())
        self.register(ReplaceConvolutionByIm2Col())
        self.register(ReplaceLinearBySGEMM())
        self.register(FixSGEMMTextureShape())
        self.register(RemoveLastSoftmax())
