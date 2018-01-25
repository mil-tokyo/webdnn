import keras

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output


@KerasConverter.register_handler("Model")
@KerasConverter.register_handler("Sequential")
def _convert_model(converter: KerasConverter, k_op: "keras.models.Model"):
    graph = converter.convert(k_op)

    for v in graph.inputs:
        for attr in v.get_attribute(Input):
            v.attributes.remove(attr)

    for v in graph.outputs:
        for attr in v.get_attribute(Output):
            v.attributes.remove(attr)

    # Initial state of nested model
    #
    #    Global Model : [layer] -> tensor(A) -> [...........Model..........]
    #                 :
    #     Local Model :            tensor(B) -> [layer] -> tensor -> [layer] -> tensor(C)
    #

    # 1. Replace local input variable (converted from tensor(B)) into global input variable (converted from tensor(A))
    #
    #    Global Model : [layer] -> tensor(A) -> [...........Model..........]
    #                 :             |
    #     Local Model :             +---------> [layer] -> tensor -> [layer] -> tensor(C)
    #
    global_inputs = [converter.get_variable(tensor) for tensor in converter.get_input_tensor(k_op)]
    for global_variable, local_variable in zip(global_inputs, graph.inputs):
        local_variable.order.unify(global_variable.order)
        local_variable.replace(global_variable)

    # 2. Register local output variable (converted from tensor(C)) as the global output variable
    #
    #    Global Model : [layer] -> tensor(A)                                     +--------->
    #                 :             |                                            |
    #     Local Model :             +---------> [layer] -> tensor -> [layer] -> tensor(C)
    #
    global_outputs = converter.get_output_tensor(k_op)
    for global_tensor, local_variable in zip(global_outputs, graph.outputs):
        converter.set_variable(global_tensor, local_variable)


# noinspection PyUnusedLocal
@KerasConverter.register_handler("InputLayer")
def _convert_input_layer(converter: KerasConverter, k_op: "keras.layers.InputLayer"):
    pass
