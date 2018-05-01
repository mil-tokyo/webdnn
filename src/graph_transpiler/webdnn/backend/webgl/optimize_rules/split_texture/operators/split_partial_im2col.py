from typing import NamedTuple, List, Sequence

from webdnn.backend.webgl.operators.partial_im2col import PartialIm2Col
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.util.assertion import UnexpectedAndPleaseReportError


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


def split_partial_im2col(graph: Graph, op: PartialIm2Col, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    im = op.inputs["im"]
    cols = [op.outputs[f"col{i}"] for i in range(len(op.outputs))]
    sections = op.sections

    if v == im:
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    elif v in cols:
        op.remove_all()

        if axis == op.axis:
            """
            before)
                                +- col0
                                |
            im -{PartialIm2Col}-+- col1
                                |
                                +- col2

            after)
                                +- col0
                                |
                                +- col1_0
            im -{PartialIm2Col}-+
                                +- col1_1
                                |
                                +- col2
            """
            target_i = cols.index(v)

            s_insert = (0 if target_i == 0 else sections[target_i - 1]) + s1
            new_sections = list(sections)
            new_sections.insert(target_i, s_insert)

            cols.pop(target_i)
            cols.insert(target_i + 0, v_pair[0])
            cols.insert(target_i + 1, v_pair[1])

            new_cols = PartialIm2Col(None,
                                     ksize=op.ksize, stride=op.stride, padding=op.padding,
                                     dilation_rate=op.dilation_rate,
                                     axis=axis, sections=new_sections)(im)
            for col, new_col in zip(cols, new_cols):
                OptimizeRule.replace_variable(graph, new_col, col)

        else:
            raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    else:
        raise UnexpectedAndPleaseReportError
