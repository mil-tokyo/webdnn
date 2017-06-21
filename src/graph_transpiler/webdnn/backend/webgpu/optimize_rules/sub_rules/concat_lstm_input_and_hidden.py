from typing import Tuple

import numpy as np

from webdnn.backend.webgpu.attributes.lstm_optimized import LSTMOptimized
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import OrderCN, OrderNC
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class ConcatLSTMInputAndHidden(OptimizeRule):
    """
    In typical LSTM, input gate signal(v_i), forget gate signal(v_f), cell update signal(v_a), and output gate signal(v_o) are calculated
    as follows:

        v_i = w_i * x + w'_i * h
        v_f = w_f * x + w'_f * h
        v_a = w_a * x + w'_a * h
        v_o = w_o * x + w'_o * h

    typical LSTM implementation combine i, f, a, o into single tensor as follows:

        v = W * x + W' * h

    This optimize rule concat W and W', and x and y

        v = W_all * XH

    Also this optimize rule append 2 additional inputs:

        workspace:
            store the data of product of W_all and XH (=v)

        cell:
            variable to store the temporal cell state
    """

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not (flags.optimize.OPTIMIZE and flags.optimize.CONCAT_LSTM_INPUT_AND_HIDDEN):
            return graph, False

        flag_changed = False
        for match in traverse.search_sub_structure(graph, [LSTM]):
            lstm = match[0]  # type: LSTM

            if lstm.has_attribute(LSTMOptimized):
                continue

            x = lstm.inputs["x"]
            w_input = lstm.inputs["w_input"]
            w_hidden = lstm.inputs["w_hidden"]
            if not isinstance(w_input, ConstantVariable) or not isinstance(w_hidden, ConstantVariable):
                continue

            attr = LSTMOptimized(lstm)

            N = x.shape_dict[Axis.N]
            C1 = attr.C1
            C2 = attr.C2

            x_and_h = Variable([N, C1 + C2], OrderNC)
            workspace = Variable([N, 4 * C2], OrderNC)
            cell = Variable([N, C2], OrderNC)

            w_input.change_order(OrderCN)
            w_hidden.change_order(OrderCN)
            w_all = ConstantVariable(np.vstack([w_input.data, w_hidden.data]), OrderCN)

            lstm.remove_input(w_input)
            lstm.remove_input(w_hidden)
            lstm.append_input("x_and_h", x_and_h)
            lstm.append_input("workspace", workspace)
            lstm.append_input("cell", cell)
            lstm.append_input("w_all", w_all)
            lstm.attributes.add(attr)

            flag_changed = True

        return graph, flag_changed