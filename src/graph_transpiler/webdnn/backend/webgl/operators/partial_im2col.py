from typing import Optional, List, Tuple

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.util import IntOrTuple, to_tuple
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


class PartialIm2Col(Operator):
    """
    This operator works basically same as Im2Col, but compute for only specified output patch.

    example)

    ... code::

        im = Variable((1,64,64,8), OrderNHWC)
        op = PartialIm2Col(None, ksize=3, stride=1, padding=1, dilation_rate=1, axis=Axis.W, sections =[32])

        col1, col2 = op(im)

        col1.order == OrderNHWC
        col1.shape == col2.shape == [1, 64, 32, 8*3*3]
    """

    def __init__(self, name: Optional[str], ksize: IntOrTuple, stride: IntOrTuple, padding: IntOrTuple,
                 dilation_rate: IntOrTuple, sections: List[int], axis: Axis):
        super().__init__(name)
        self.parameters["ksize"] = to_tuple(ksize)
        self.parameters["stride"] = to_tuple(stride)
        self.parameters["padding"] = to_tuple(padding)
        self.parameters["dilation_rate"] = to_tuple(dilation_rate)
        self.parameters["sections"] = list(sections)
        self.parameters["axis"] = axis
        if axis != Axis.N:
            self.attributes.add(Tensorwise(Axis.N))
        if axis != Axis.C:
            self.attributes.add(Tensorwise(Axis.C))

    def __call__(self, im: Variable):
        N = im.shape_dict[Axis.N]
        H2 = (im.shape_dict[Axis.H] + 2 * self.PH - self.WH) // self.SH + 1
        W2 = (im.shape_dict[Axis.W] + 2 * self.PW - self.WW) // self.SW + 1
        C1 = im.shape_dict[Axis.C]
        col = Variable([N, H2, W2, self.KH, self.KW, C1], Order([Axis.N, Axis.H, Axis.W, Axis.KH, Axis.KW, Axis.C]))

        sections = [0] + self.parameters["sections"] + [col.shape_dict[self.axis]]
        cols = []  # type: List[Tuple[str, Variable]]

        for i, i_from in enumerate(sections[:-1]):
            i_to = sections[i + 1]
            assert i_from < i_to, f"[SplitAxis] sections must be sorted ascending order: sections={sections}, sections[{i}]={i_from}, " \
                                  f"sections[{i+1}]={i_to}"

            partial_col_shape = list(col.shape)
            partial_col_shape[col.order.axes_dict[self.axis]] = i_to - i_from
            partial_col = Variable(partial_col_shape, col.order)

            cols.append((f"col{i}", partial_col))

        self.append_input(f"im", im)
        for key, col in cols:
            self.append_output(key, col)
        return tuple(col for _, col in cols)

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]

    @property
    def sections(self) -> List[int]:
        return list(self.parameters["sections"])

    @property
    def ksize(self) -> Tuple[int, int]:
        return self.parameters["ksize"]

    @property
    def stride(self) -> Tuple[int, int]:
        return self.parameters["stride"]

    @property
    def padding(self) -> Tuple[int, int]:
        return self.parameters["padding"]

    @property
    def dilation_rate(self) -> Tuple[int, int]:
        return self.parameters["dilation_rate"]

    @property
    def KH(self) -> int:
        return self.parameters["ksize"][0]

    @property
    def KW(self) -> int:
        return self.parameters["ksize"][1]

    @property
    def SH(self) -> int:
        return self.parameters["stride"][0]

    @property
    def SW(self) -> int:
        return self.parameters["stride"][1]

    @property
    def PH(self) -> int:
        return self.parameters["padding"][0]

    @property
    def PW(self) -> int:
        return self.parameters["padding"][1]

    @property
    def DH(self) -> int:
        return self.parameters["dilation_rate"][0]

    @property
    def DW(self) -> int:
        return self.parameters["dilation_rate"][1]

    @property
    def WH(self) -> int:
        """
        Input window height considering dilation.
        Returns:

        """
        return self.DH * (self.KH - 1) + 1

    @property
    def WW(self) -> int:
        """
        Input window width considering dilation.
        Returns:

        """
        return self.DW * (self.KW - 1) + 1
