try:
    import keras
except ImportError as e:
    pass

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.order import OrderNC, OrderCN, OrderNT


@KerasConverter.register_handler("Embedding")
def _convert_embedding(converter: KerasConverter, k_op: "keras.layers.Embedding"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    if x.order == OrderNC:
        x, = ReinterpretAxis(None, in_order=OrderNC, out_order=OrderNT)(x)

    w = converter.convert_to_constant_variable(k_op.embeddings, OrderCN)

    y, = Embedding(None)(x, w)
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)
