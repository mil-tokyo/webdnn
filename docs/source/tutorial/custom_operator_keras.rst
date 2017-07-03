How to Support Your Custom Keras Layer
--------------------------------------

How to Implement Custom IR Operator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO

How to Implement Custom Converter Handler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, you have to load input variables. KerasConverter convert layers from input to output. Therefore, input variables
have always converted before your handler is called. Because KerasConverter manages converted variables by dictionary
with key of related `tf.tensor`, you have to get input tensors first. You can do that easily by using
:func:`converter.get_input_tensor(k_op) <webdnn.frontend.keras.KerasConverter.get_input_tensor>`.::

    @KerasConverter.register("SomeLayer")
    def my_handler(converter: KerasConverter, k_op: keras.layers.SomeLayer):
        input_tensors = converter.get_input_tensor(k_op)
        input_variables = [converter.get_variable(tensor) for tensor in input_tensors]

If number of inputs is always 1, it can be written as follows.::

    @KerasConverter.register("SomeLayer")
    def my_handler(converter: KerasConverter, k_op: keras.layers.SomeLayer):
        x = converter.get_variable(converter.get_input_tensor(k_op)[0])

Next, convert all parameters of the keras layer into
:class:`ConstantVariable <webdnn.graph.variables.constant_variable.ConstantVariable>`.
:func:`converter.convert_to_constant_variable(tf_var, order) <webdnn.frontend.keras.KerasConverter.convert_to_constant_variable>`
is all you have to do.::

    w = converter.convert_to_constant_variable(k_op.kernel, OrderNHWC)

Then, all input variables are prepared. Let's construct graph fragment.::

    operator = YourOperator("your operator", some_hyper_parameters=k_op.some_hyper_parameters)
    y, = operator(x, w)

Finally, register the output WebDNN variable with the key of related output tensor. You can get output tensor by
:func:`converter.get_output_tensor(k_op) <webdnn.frontend.keras.KerasConverter.get_output_tensor>`.::

    y_tensor = converter.get_output_tensor(k_op)[0]
    converter.set_variable(y_tensor, y)

Complete code is as follows.::

    @KerasConverter.register("SomeLayer")
    def my_handler(converter: KerasConverter, k_op: keras.layers.SomeLayer):
        x = converter.get_variable(converter.get_input_tensor(k_op)[0])

        w = converter.convert_to_constant_variable(k_op.kernel, OrderNHWC)

        operator = YourOperator("your operator", some_hyper_parameters=k_op.some_hyper_parameters)

        y, = operator(x, w)
        converter.set_variable(converter.get_output_tensor(k_op)[0], y)

How to Implement Custom Generator Handler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO
