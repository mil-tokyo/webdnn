from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR
from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_nonsense_channel_mode_conversion import \
    SimplifyNonsenseChannelModeConversion
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.order import OrderNCHW, OrderNHWC
from webdnn.graph.variable import Variable


def test_r2rgba():
    """test_r2rgba

    before)

    v0 -{ConvertRGBAtoR}- v1 -{ConvertRtoRGBA}- v2

    after)

    v0 -{Transpose}- v2

    """
    v0 = Variable((2, 3, 4, 5), OrderNCHW)
    v1, = ConvertRGBAtoR(None)(v0)
    v2, = ConvertRtoRGBA(None)(v1)
    v2.change_order(OrderNHWC)

    v0_original_order = v0.order
    v2_original_order = v2.order

    graph = Graph([v0], [v2])
    SimplifyNonsenseChannelModeConversion().optimize(graph)

    assert len(graph.inputs) == 1 and graph.inputs[0] == v0
    assert len(graph.outputs) == 1 and graph.outputs[0] == v2

    assert v0.order == v0_original_order

    assert len(traverse.listup_operators(graph)) == 1

    assert isinstance(v2.output_from, Transpose) and v2.output_from.inputs["x0"] == v0
    assert v2.order == v2_original_order


def test_rgba2r():
    """test_rgba2r

    before)

    v0 -{ConvertRtoRGBA}- v1 -{ConvertRGBAtoR}- v2

    after)

    v0 -{Transpose}- v2

    """
    v0 = Variable((2, 3, 4, 5), OrderNCHW)
    v1, = ConvertRtoRGBA(None)(v0)
    v2, = ConvertRGBAtoR(None)(v1)
    v2.change_order(OrderNHWC)

    v0_original_order = v0.order
    v2_original_order = v2.order

    graph = Graph([v0], [v2])
    SimplifyNonsenseChannelModeConversion().optimize(graph)

    assert len(graph.inputs) == 1 and graph.inputs[0] == v0
    assert len(graph.outputs) == 1 and graph.outputs[0] == v2

    assert v0.order == v0_original_order

    assert len(traverse.listup_operators(graph)) == 1

    assert isinstance(v2.output_from, Transpose) and v2.output_from.inputs["x0"] == v0
    assert v2.order == v2_original_order
