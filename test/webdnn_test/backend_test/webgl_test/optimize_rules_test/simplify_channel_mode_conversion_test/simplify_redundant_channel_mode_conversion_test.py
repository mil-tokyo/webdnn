from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_redundant_channel_mode_conversion import \
    SimplifyRedundantChannelModeConversion
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.order import OrderNCHW
from webdnn.graph.variable import Variable


def test_r2rgba_1():
    """test_r2rgba_1

    before)

    v0[R] -{ConvertRtoRGBA}- v1[RGBA] -{ConvertRtoRGBA}- v2[RGBA]

    after)

    v0[R] -{ConvertRtoRGBA}- v1[RGBA] -{ConvertRGBAtoR}- v3[R] -{Transpose}- v4[R] -{ConvertRtoRGBA}- v2[RGBA]
    """
    v0 = Variable((2, 3, 4, 5), OrderNCHW)
    v1, = ConvertRtoRGBA(None)(v0)
    v2, = ConvertRtoRGBA(None)(v1)

    graph = Graph([v0], [v2])
    SimplifyRedundantChannelModeConversion().optimize(graph)

    assert len(graph.inputs) == 1 and graph.inputs[0] == v0
    assert len(graph.outputs) == 1 and graph.outputs[0] == v2

    new_ops = traverse.listup_operators(graph)
    assert len(new_ops) == 4
    assert isinstance(new_ops[0], ConvertRtoRGBA)
    assert isinstance(new_ops[1], ConvertRGBAtoR)
    assert isinstance(new_ops[2], Transpose)
    assert isinstance(new_ops[3], ConvertRtoRGBA)


def test_r2rgba_2():
    """test_r2rgba_2

    before)

    v0[R] -{ConvertRtoRGBA}- v1[RGBA] -{ConvertRtoRGBA}- v2[RGBA] -{ConvertRtoRGBA} -v3[RGBA]

    after)

    v0[R] -{ConvertRtoRGBA}- v1[RGBA] -{ConvertRGBAtoR}- v3[R] -{Transpose}- v4[R] -{ConvertRtoRGBA}- v2[RGBA] -

    - v2[RGBA] -{ConvertRGBAtoR}- v5[R] -{Transpose}- v6[R] -{ConvertRtoRGBA}- v3[RGBA]
    """
    v0 = Variable((2, 3, 4, 5), OrderNCHW)
    v1, = ConvertRtoRGBA(None)(v0)
    v2, = ConvertRtoRGBA(None)(v1)
    v3, = ConvertRtoRGBA(None)(v2)

    graph = Graph([v0], [v3])
    SimplifyRedundantChannelModeConversion().optimize(graph)

    assert len(graph.inputs) == 1 and graph.inputs[0] == v0
    assert len(graph.outputs) == 1 and graph.outputs[0] == v3

    new_ops = traverse.listup_operators(graph)
    assert len(new_ops) == 7
    assert isinstance(new_ops[0], ConvertRtoRGBA)
    assert isinstance(new_ops[1], ConvertRGBAtoR)
    assert isinstance(new_ops[2], Transpose)
    assert isinstance(new_ops[3], ConvertRtoRGBA)
    assert isinstance(new_ops[4], ConvertRGBAtoR)
    assert isinstance(new_ops[5], Transpose)
    assert isinstance(new_ops[6], ConvertRtoRGBA)


def test_rgba2r_1():
    """test_rgba2r_1

    before)

    v0[R] -{ConvertRGBAtoR}- v1[R]

    after)

    v0[R] -{Transpose}- v1[R]
    """
    v0 = Variable((2, 3, 4, 5), OrderNCHW)
    v1, = ConvertRGBAtoR(None)(v0)

    graph = Graph([v0], [v1])
    SimplifyRedundantChannelModeConversion().optimize(graph)

    assert len(graph.inputs) == 1 and graph.inputs[0] == v0
    assert len(graph.outputs) == 1 and graph.outputs[0] == v1

    new_ops = traverse.listup_operators(graph)
    assert len(new_ops) == 1
    assert isinstance(new_ops[0], Transpose)


def test_rgba2r_2():
    """test_rgba2r_2

    before)

    v0[R] -{ConvertRGBAtoR}- v1[R] -{ConvertRGBAtoR}- v2[R]

    after)

    v0[R] -{Transpose}- v1[R] -{Transpose}- v2[R]
    """
    v0 = Variable((2, 3, 4, 5), OrderNCHW)
    v1, = ConvertRGBAtoR(None)(v0)
    v2, = ConvertRGBAtoR(None)(v1)

    graph = Graph([v0], [v2])
    SimplifyRedundantChannelModeConversion().optimize(graph)

    assert len(graph.inputs) == 1 and graph.inputs[0] == v0
    assert len(graph.outputs) == 1 and graph.outputs[0] == v2

    new_ops = traverse.listup_operators(graph)
    assert len(new_ops) == 2
    assert isinstance(new_ops[0], Transpose)
    assert isinstance(new_ops[1], Transpose)
