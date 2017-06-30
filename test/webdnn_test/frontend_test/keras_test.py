import logging

logging.getLogger("tensorflow").setLevel(logging.WARNING)

import keras

from webdnn.graph.axis import Axis
from webdnn.graph.operators.linear import Linear
from webdnn.graph.order import OrderNC
from webdnn.graph.variable import Variable
from webdnn.frontend.keras2 import KerasConverter
from webdnn.graph import traverse


def test_simplest():
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(32, input_shape=(16,)))

    graph = KerasConverter().convert(model)
    traverse.dump(graph)

    assert len(graph.inputs) == 1
    assert graph.inputs[0].order == OrderNC
    assert graph.inputs[0].shape_dict[Axis.C] == 16

    assert len(graph.outputs) == 1
    assert graph.outputs[0].order == OrderNC
    assert graph.outputs[0].shape_dict[Axis.C] == 32

    match = traverse.search_sub_structure(graph, [Variable, Linear, Variable])
    print(match)
    assert len(match) == 1
    nodes = match[0]

    assert nodes[0] == nodes[1].inputs["x"] == graph.inputs[0]

    assert set(nodes[1].inputs["w"].order.axes) == {Axis.N, Axis.C}
    assert nodes[1].inputs["w"].shape_dict[Axis.N] == 32
    assert nodes[1].inputs["w"].shape_dict[Axis.C] == 16

    assert nodes[1].outputs["y"] == nodes[2] == graph.outputs[0]


def test_sequential_deep():
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(32, input_shape=(16,)))
    model.add(keras.layers.Dense(64))
    model.compile(loss="categorical_crossentropy",
                  optimizer=keras.optimizers.RMSprop(),
                  metrics=["accuracy"])

    graph = KerasConverter().convert(model)
    traverse.dump(graph)

    assert len(graph.inputs) == 1
    assert graph.inputs[0].order == OrderNC
    assert graph.inputs[0].shape_dict[Axis.C] == 16

    assert len(graph.outputs) == 1
    assert graph.outputs[0].order == OrderNC
    assert graph.outputs[0].shape_dict[Axis.C] == 64

    match = traverse.search_sub_structure(graph, [Variable, Linear, Variable, Linear, Variable])
    assert len(match) == 1
    nodes = match[0]

    assert nodes[0] == nodes[1].inputs["x"] == graph.inputs[0]

    assert set(nodes[1].inputs["w"].order.axes) == {Axis.N, Axis.C}
    assert nodes[1].inputs["w"].shape_dict[Axis.N] == 32
    assert nodes[1].inputs["w"].shape_dict[Axis.C] == 16

    assert nodes[1].outputs["y"] == nodes[2] == nodes[3].inputs["x"]
    assert set(nodes[2].order.axes) == {Axis.N, Axis.C}
    assert nodes[2].shape_dict[Axis.C] == 32

    assert set(nodes[3].inputs["w"].order.axes) == {Axis.N, Axis.C}
    assert nodes[3].inputs["w"].shape_dict[Axis.N] == 64
    assert nodes[3].inputs["w"].shape_dict[Axis.C] == 32

    assert nodes[3].outputs["y"] == nodes[4] == graph.outputs[0]
