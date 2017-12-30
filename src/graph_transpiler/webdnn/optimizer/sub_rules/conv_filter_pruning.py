from typing import Tuple, Optional, List

import numpy as np

from webdnn.graph import traverse
from webdnn.graph.attribute import Attribute
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class ConvFilterPruned(Attribute):
    def __init__(self, base: Convolution2D, limit: int, removed: int = 0):
        if base.has_attribute(ConvFilterPruned):
            raise ValueError(f"\'ConvFilterPruned\' attribute has been already registered to {base}.")

        super(ConvFilterPruned, self).__init__(base)
        self.limit = limit  # type: int
        self.removed = removed  # type: int

    def __str__(self):
        return f"ConvFilterPruned[{self.removed}/{self.limit}]"

    @staticmethod
    def has(base: Convolution2D):
        return base.has_attribute(ConvFilterPruned)

    @staticmethod
    def get(base: Convolution2D):
        if base.has_attribute(ConvFilterPruned):
            return base.get_attribute(ConvFilterPruned)[0]


def _find_conv2(conv1: Convolution2D) -> Optional[List[Variable]]:
    y = conv1.outputs["y"]
    parameters = []  # type: List[Variable]

    while True:
        if len(y.input_to) != 1:
            # must be sequential
            return None

        next_op = list(y.input_to)[0]

        if isinstance(next_op, Convolution2D) and isinstance(next_op.inputs["w"], ConstantVariable):
            # sub graph is finished
            w = next_op.inputs["w"]  # type: ConstantVariable
            parameters.append(w)
            parameters.append(y)
            return parameters

        if not isinstance(next_op, Elementwise):
            # intermediate operator must be elementwise  # FIXME: Is this constraints correct?
            return None

        if not all(isinstance(v, ConstantVariable) or v == y for v in next_op.inputs.values()):
            return None

        for v in next_op.inputs.values():
            if (not isinstance(v, ConstantVariable)) and (v is not y):
                # all input of intermediate variable without :code:`y` must be constant variables
                # TODO: Residual block
                return None

            parameters.append(v)

        y = next_op.outputs["y"]


class ConvFilterPruning(OptimizeRule):
    """
    In follow sub graph structure, some filter in conv1 (and related parts of filters in conv2) can be pruned.

    .. code-block::

        -{conv1}-{elementwise}- ... -{elementwise}-{conv2}-

    This optimize rule is based on [1].

    [1] Hao et al. "Pruning Filters for Efficient Convnets", ICLR 2017.
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.CONV_FILTER_PRUNING
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        REMOVE_RATE = 0.10  # remove 10% of filters

        flag_changed = False

        for conv1 in traverse.filter_nodes(traverse.listup_operators(graph), Convolution2D):
            parameters = _find_conv2(conv1)
            if parameters is None:
                continue

            w1 = conv1.inputs["w"]  # type: ConstantVariable
            filter_weights = np.abs(ConstantVariable(w1.data, w1.order).change_order(OrderNCHW).data).sum(axis=(2, 3)).sum(axis=1)

            if ConvFilterPruned.has(conv1):
                attr = ConvFilterPruned.get(conv1)
            else:
                attr = ConvFilterPruned(conv1, int(filter_weights.size * REMOVE_RATE))
                conv1.attributes.add(attr)

            if attr.removed >= attr.limit:
                break

            flag_changed = True
            c2_removed_list = np.argsort(filter_weights, axis=0)[:(attr.limit - attr.removed)].tolist()
            attr.removed += len(c2_removed_list)

            for c2_removed in sorted(c2_removed_list, reverse=True):
                new_w1 = ConstantVariable(np.delete(w1.data, c2_removed, axis=w1.order.axes_dict[Axis.N]), w1.order)
                OptimizeRule.replace_variable(graph, w1, new_w1, with_assert=False)
                w1 = new_w1

                new_parameters = []
                for v in parameters:
                    if Axis.C not in v.order.axes:
                        # v don't has Axis.C (= v will be broadcasted along to Axis.C)
                        continue

                    if isinstance(v, ConstantVariable):
                        new_v = ConstantVariable(np.delete(v.data, c2_removed, axis=v.order.axes_dict[Axis.C]), v.order)
                        OptimizeRule.replace_variable(graph, v, new_v, with_assert=False)
                        new_parameters.append(new_v)

                    else:
                        new_shape = list(v.shape)
                        new_shape[v.order.axes_dict[Axis.C]] -= 1
                        new_v = Variable(new_shape, v.order)
                        OptimizeRule.replace_variable(graph, v, new_v, with_assert=False)
                        new_parameters.append(new_v)

                parameters = new_parameters

        return graph, flag_changed
