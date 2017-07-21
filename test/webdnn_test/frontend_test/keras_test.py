from test.runtime.frontend_test.keras_test.util import keras
from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph import traverse
from webdnn.graph.operators.elementwise_add import ElementwiseAdd
from webdnn.graph.operators.linear import Linear
from webdnn.util.assertion import assert_equal


def test_sequential_one_layer():
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(4, use_bias=False, activation=None, input_shape=(2,)))
    model.build()

    graph = KerasConverter(batch_size=1).convert(model)

    assert_equal(len(graph.inputs), 1)

    ops = traverse.listup_operators(graph)
    assert_equal(len(ops), 1)
    assert_equal(type(ops[0]), Linear)

    assert_equal(len(graph.outputs), 1)


def test_sequential_multi_layer():
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(4, use_bias=False, activation=None, input_shape=(2,)))
    model.add(keras.layers.Dense(8, use_bias=False, activation=None))
    model.build()

    graph = KerasConverter(batch_size=1).convert(model)

    assert_equal(len(graph.inputs), 1)

    ops = traverse.listup_operators(graph)
    assert_equal(len(ops), 2)
    assert_equal(type(ops[0]), Linear)
    assert_equal(type(ops[1]), Linear)

    assert_equal(len(graph.outputs), 1)


def test_use_same_layer_twice():
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(4, use_bias=False, activation=None, input_shape=(2,)))

    layer = keras.layers.Dense(4, use_bias=False, activation=None)

    model.add(layer)
    model.add(layer)

    model.build()

    graph = KerasConverter(batch_size=1).convert(model)

    assert_equal(len(graph.inputs), 1)

    ops = traverse.listup_operators(graph)
    assert_equal(len(ops), 3)
    assert_equal(type(ops[0]), Linear)
    assert_equal(type(ops[1]), Linear)
    assert_equal(type(ops[2]), Linear)
    assert_equal(len(graph.outputs), 1)


def test_nested_model():
    model1 = keras.models.Sequential()
    model1.add(keras.layers.Dense(8, use_bias=False, activation=None, input_shape=(4,)))

    model2 = keras.models.Sequential()
    model2.add(keras.layers.Dense(4, use_bias=False, activation=None, input_shape=(2,)))
    model2.add(model1)
    model2.add(keras.layers.Dense(16, use_bias=False, activation=None))
    model2.build()

    graph = KerasConverter(batch_size=1).convert(model2)

    assert_equal(len(graph.inputs), 1)

    ops = traverse.listup_operators(graph)
    assert_equal(len(ops), 3)
    assert_equal(type(ops[0]), Linear)
    assert_equal(type(ops[1]), Linear)
    assert_equal(type(ops[2]), Linear)

    assert_equal(len(graph.outputs), 1)


def test_residual():
    x = keras.layers.Input(shape=(4,))
    h1 = keras.layers.Dense(8, use_bias=False, activation=None)(x)
    h21 = keras.layers.Dense(4, use_bias=False, activation=None)(h1)
    h22 = keras.layers.Dense(4, use_bias=False, activation=None)(h1)
    y = keras.layers.add([h21, h22])
    model = keras.models.Model([x], [y])
    model.build(input_shape=(1, 4))

    graph = KerasConverter(batch_size=1).convert(model)

    assert_equal(len(graph.inputs), 1)

    ops = traverse.listup_operators(graph)
    assert_equal(len(ops), 4)
    assert_equal(type(ops[0]), Linear)
    assert_equal(type(ops[1]), Linear)
    assert_equal(type(ops[2]), Linear)
    assert_equal(type(ops[3]), ElementwiseAdd)

    assert_equal(len(graph.outputs), 1)
