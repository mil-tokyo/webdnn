import numpy as np
from nose import with_setup

from test.util import FlagManager
from webdnn.backend.webgpu.operators.sgemm import Sgemm
from webdnn.backend.webgpu.optimize_rules.sub_rules.concat_sgemm_bias import ConcatSgemmBias
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.order import OrderNC, OrderC
from webdnn.graph.traverse import listup_operators
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags


class ConcatSgemmBiasFlagManager(FlagManager):
    def get(self) -> bool:
        return flags.optimize.CONCAT_SGEMM_BIAS

    def set(self, value: bool):
        flags.optimize.CONCAT_SGEMM_BIAS = value


flag_manager = ConcatSgemmBiasFlagManager()


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_single_bias():
    sgemm = Sgemm(None, M=5, N=5, K=5, out_shape=[5, 5], out_order=OrderNC, transpose_A=True, transpose_B=True)
    bias = AxiswiseBias(None, axis=Axis.C)

    x = Variable([5, 5], OrderNC)

    w_shape = [5, 5]
    w_size = np.prod(w_shape)  # type: int
    w = ConstantVariable(np.arange(w_size).reshape(w_shape), OrderNC)
    w_data = w.data.copy()

    b_shape = [5]
    b_size = np.prod(b_shape)  # type: int
    b = ConstantVariable(np.arange(b_size).reshape(b_shape), OrderC)
    b_data = b.data.copy()

    h, = sgemm(x, w)
    y, = bias(h, b)

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = ConcatSgemmBias().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], Sgemm)
    assert len(graph.outputs) == 1 and ops[0].outputs["C"] == graph.outputs[0]
    assert "B" in ops[0].inputs and np.all(np.equal(ops[0].inputs["B"].data, w_data))
    assert "b" in ops[0].inputs and np.all(np.equal(ops[0].inputs["b"].data, b_data))


@with_setup(flag_manager.setup, flag_manager.teardown)
def test_double_bias():
    sgemm = Sgemm(None, M=5, N=5, K=5, out_shape=[5, 5], out_order=OrderNC, transpose_A=True, transpose_B=True)
    bias1 = AxiswiseBias(None, axis=Axis.C)
    bias2 = AxiswiseBias(None, axis=Axis.C)

    x = Variable([5, 5], OrderNC)

    w_shape = [5, 5]
    w_size = np.prod(w_shape)  # type: int
    w = ConstantVariable(np.arange(w_size).reshape(w_shape), OrderNC)
    w_data = w.data.copy()

    b1_shape = [5]
    b1_size = np.prod(b1_shape)  # type: int
    b1 = ConstantVariable(np.arange(b1_size).reshape(b1_shape), OrderC)
    b1_data = b1.data.copy()

    b2_shape = [5]
    b2_size = np.prod(b2_shape)  # type: int
    b2 = ConstantVariable(np.arange(b2_size).reshape(b2_shape), OrderC)
    b2_data = b2.data.copy()

    h, = sgemm(x, w)
    h, = bias1(h, b1)
    y, = bias2(h, b2)

    graph = Graph([x], [y])

    flag_changed = True
    while flag_changed:
        graph, flag_changed = ConcatSgemmBias().optimize(graph)

    ops = listup_operators(graph)
    assert len(ops) == 1 and isinstance(ops[0], Sgemm)
    assert len(graph.outputs) == 1 and ops[0].outputs["C"] == graph.outputs[0]
    assert "B" in ops[0].inputs and np.all(np.equal(ops[0].inputs["B"].data, w_data))
    assert "b" in ops[0].inputs and np.all(np.equal(ops[0].inputs["b"].data, b1_data + b2_data))
