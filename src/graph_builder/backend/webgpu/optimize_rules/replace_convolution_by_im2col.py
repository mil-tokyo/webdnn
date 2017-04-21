from graph_builder.backend.webgpu import operators as webgpu_O
from graph_builder.graph import Operator, operators as O
from graph_builder.graph.operators import attributes as A
from graph_builder.optimizer import OptimizeRule, util


class ReplaceConvolutionByIm2Col(OptimizeRule):
    """
    Convolution2DをIm2Col + sgemmに置換する
    """

    def __call__(self, graph: Operator):
        flag_changed = False
        for op in util.listup_operator_in_order(graph):
            if not isinstance(op, O.Convolution2D):
                continue

            conv = op  # type: O.Convolution2D

            x = conv.inputs["x"]
            w = conv.inputs["w"]
            y = conv.outputs["y"]

            flag_changed = True
            conv.remove_all()

            # connect im2col and sgemm
            im2col = webgpu_O.Im2Col("im2col", {
                "ksize": conv.ksize,
                "stride": conv.stride,
                "padding": conv.padding,
            })
            sgemm = webgpu_O.Sgemm("sgemm")

            col, = im2col(x)
            _dummy_y, = sgemm(col, w)

            sgemm.replace_output(_dummy_y, y)

        return graph, flag_changed
