from typing import Tuple

import numpy as np

from webdnn.graph import traverse
from webdnn.graph.attribute import Attribute
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class Convolution2DSvdCompressed(Attribute):
    pass


def _svd(W, rate):
    if not 0 <= rate <= 1:
        raise ValueError(f"[Convolution2DSvdCompression] The parameter \"rate\" must be in from 0 to 1: (rate)={rate}")

    U, s, V = np.linalg.svd(W, full_matrices=False)

    n = 0
    while True:
        n += 1
        if s[:n].sum() >= s.sum() * rate:
            break

    return U[:, :n], np.dot(np.diag(s[:n]), V[:n, :])


class Convolution2DSvdCompression(OptimizeRule):
    """
    Convolution2D calculates each output element as follows,

    .. math::

        Y_{n,c2,x,y} = \sum_{c1 \in C1} \sum_{r \in R} \sum_{s \in S} W_{c1,c2,r,s} X_{n,c1,x+r,y+s}

    This optimization rule decomposes filter matrix :math:`W` into 2 matrices :math:`W_expand` and :math:`W_squeeze` as follows,

    .. math::

        W \approx W_expand * W_squeeze

    where,
        - :math:`W \in R^{C2 \cdot R \cdot S \cross C1}` is original filter matrix.
        - :math:`W_{expand} \in R^{C2 \cdot R \cdot S \cross C3}` is expansion matrix.
        - :math:`W_{squeeze} \in R^{C3 \cross C1}` is squeezing matrix.
        - :math:`C1` is number of input channels.
        - :math:`C2` is number of output channels.
        - :math:`C3` is number of output channels of squeeze module.
        - :math:`(R, S)` is size of convolution window.

    The decomposition is performed by SVD.

    Then, convolution operation can be written as follows,

    .. math::

        Y_{n,c2,x,y}
            &= \sum_{c1 \in C1} \sum_{r \in R} \sum_{s \in S} W_{c1,c2,r,s} X_{n,c1,x+r,y+s}
            &= \sum_{c1 \in C1} \sum_{r \in R} \sum_{s \in S} \left( \sum_{c3 \in C3} W_{expand,c2,c3,r,s} W_{squeeze,c3,c1} \right) X_{n,c1,x+r,y+s}
            &= \sum_{c3 \in C3} \sum_{r \in R} \sum_{s \in S} W_{expand,c2,c3,r,s} \left( \sum_{c1 \in C1} W_{squeeze,c3,c1} X_{n,c1,x+r,y+s} \right)

    .. math::

        \therefore Y = W_expand * (W_squeeze \cdot X)

    Therefore, convolution2D operator is converted as follows

    .. code-block:: text

        before)

        X --+
            +-{conv}-Y
        W --+

    .. code-block:: text

        after)

                X --+
                    +-{conv 1x1}- H -+
        W_squeeze --+                +-{conv RxS}- Y
                           W_expand -+
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.CONV_SVD_COMPRESSION
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        for conv in traverse.filter_nodes(traverse.listup_operators(graph), Convolution2D):
            x = conv.inputs["x"]
            w = conv.inputs["w"]
            y = conv.outputs["y"]
            if not isinstance(w, ConstantVariable):
                continue

            C2 = w.shape_dict[Axis.N]
            KH = w.shape_dict[Axis.H]
            KW = w.shape_dict[Axis.W]
            C1 = w.shape_dict[Axis.C]

            if conv.has_attribute(Convolution2DSvdCompressed):
                continue

            if KH != conv.PH * 2 + 1 or KW != conv.PW * 2 + 1 or conv.SH != 1 or conv.SW != 1 or conv.DH != 1 or conv.DW != 1:
                # TODO: Is this constraint required?
                continue

            w_copy = ConstantVariable(w.data, w.order)
            w_copy.change_order(OrderNHWC)
            d = w_copy.data.reshape((C2 * KH * KW, C1))

            d_expand, d_squeeze = _svd(d, 0.5)
            C3 = d_expand.shape[1]

            """
            Computation complexity:

            before)       After)
            C1*C2*KH*KW > C1*C3 + C3*C2*KH*KW

            <=> (C1*C2*KH*KW) / (C1+C2*KH*KW) > C3
            """
            relative_complexity = (C1 * C3 + C3 * C2 * KH * KW) / (C1 * C2 * KH * KW)
            if relative_complexity >= 1:
                """
                In this case, decomposition makes convolution more complex
                """
                continue

            conv.remove_all()

            w_expand = ConstantVariable(d_expand.reshape([C2, KH, KW, C3]), OrderNHWC)
            w_squeeze = ConstantVariable(d_squeeze.reshape([C3, 1, 1, C1]), OrderNHWC)

            conv1 = Convolution2D(None, ksize=1, stride=1, padding=0, dilation_rate=1)
            conv2 = Convolution2D(None, ksize=conv.ksize, stride=conv.stride, padding=conv.padding, dilation_rate=conv.dilation_rate)

            h, = conv1(x, w_squeeze)
            y_new, = conv2(h, w_expand)

            conv1.attributes.add(Convolution2DSvdCompressed())
            conv2.attributes.add(Convolution2DSvdCompressed())
            OptimizeRule.replace_variable(graph, y_new.transpose_like(y), y)

            flag_changed = True

        return graph, flag_changed
