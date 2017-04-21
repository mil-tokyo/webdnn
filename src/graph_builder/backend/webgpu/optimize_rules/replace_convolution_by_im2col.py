from graph_builder.backend.webgpu.operators.im2col import Im2Col
from graph_builder.backend.webgpu.operators.sgemm import Sgemm
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


class ReplaceConvolutionByIm2Col(OptimizeRule):
    """
    Convolution2DをIm2Col + sgemmに置換する
    """

    def __call__(self, graph: Operator):
        flag_changed = False
        for op in util.listup_operator_in_order(graph):
            if not isinstance(op, Convolution2D):
                continue

            op: Convolution2D

            x = op.inputs["x"]
            w = op.inputs["w"]
            y = op.outputs["y"]

            flag_changed = True
            op.remove_all()

            # connect im2col and sgemm
            im2col = Im2Col("im2col", {
                "ksize": op.ksize,
                "stride": op.stride,
                "padding": op.padding,
            })
            sgemm = Sgemm("sgemm")

            col, = im2col(x)
            new_y, = sgemm(col, w)

            new_y.merge(y)

        return graph, flag_changed
