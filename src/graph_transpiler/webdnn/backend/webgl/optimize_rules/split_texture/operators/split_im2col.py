from typing import NamedTuple, List, Sequence

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.backend.webgl.operators.partial_im2col import PartialIm2Col
from webdnn.backend.webgl.optimize_rules.split_texture.check_texture_size import SplitTarget
from webdnn.graph import traverse
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.pooling_2d import Pooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.slice import Slice
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order, OrderNHWC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import console
from webdnn.util.assertion import UnexpectedAndPleaseReportError
from webdnn.util.misc import mul


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


def split_im2col(graph: Graph, op: Im2Col, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    im = op.inputs["im"]
    col = op.outputs["col"]

    op.remove_all()

    if v == col:
        """
        before)

        im -{Im2Col}- col

        after)

                            +- col_0
        im -{PartialIm2Col}-+
                            +- col_1
        """
        col_0, col_1 = PartialIm2Col(None,
                                     ksize=op.ksize, stride=op.stride, padding=op.padding,
                                     dilation_rate=op.dilation_rate,
                                     axis=axis, sections=[s1])(im)

        OptimizeRule.replace_variable(graph, col_0.transpose(v_pair[0].order), v_pair[0])
        OptimizeRule.replace_variable(graph, col_1.transpose(v_pair[1].order), v_pair[1])

    elif v == im:
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    else:
        raise UnexpectedAndPleaseReportError
