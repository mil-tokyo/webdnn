1. Elementwise Operator without Parameters
==========================================

.. toctree::
    :maxdepth: 1

In this section, you will learn about how to convert **custom keras layer which is elementwise operation with no hyper parameters**.

Complete sample code is included in :code:`/example/custom_operator/section1`.

Example: Squaring
-----------------

Let's consider to convert :code:`SquareLayer` defined as follows:

.. code::

    class SquareLayer(keras.layers.Layer):
        """
        calculate x^2 elementwisely
        """

        def call(self, x):
            return keras.backend.pow(x, 2)

To convert this layer, you have to implement 3 components: **IR operator**, **converter handler**, and **generator handler**.

.. image:: ./figures/section1_overview.png


1.1. Define Custom IR Operator
------------------------------

First, we define new :class:`~webdnn.Operator` class which represents :code:`SquareLayer` in WebDNN IR. In this case,
:class:`~webdnn.graph.operators.elementwise.Elementwise` operator base class is already defined. Therefore you can define
:code:`SquareOperator` simply as follows:

.. code::

    from webdnn.graph.operators.elementwise import Elementwise

    class SquareOperator(Elementwise):
        pass

.. image::./figures/square_operator.png
    :align: right

When :class:`~webdnn.graph.operators.elementwise.Elementwise` operator is called, each input variable is registered with the name
:code:`"x0"`, :code:`"x1"`, ..., :code:`"x{n}"`. Also output variable is registered with the name :code:`"y"`.

Because IR represents only relations between nodes(input and output variable) and operator's attribute (elementwise, inplace, etc.), you
don't need to implement computing logic here.


1.2. Define Converter Handler
-----------------------------

Next, we define converter handler which convert :code:`SquareLayer` node into :code:`SquareOperator` node.

.. code::

    from webdnn.frontend.keras.converter import KerasConverter

    @KerasConverter.register_handler("SquareLayer")
    def square_converter_handler(converter: KerasConverter, keras_layer: SquareLayer):
        keras_x = converter.get_input_tensor(keras_layer)[0]
        webdnn_x = converter.get_variable(keras_x)

        webdnn_operator = SquareOperator(None)
        webdnn_y, = webdnn_operator(webdnn_x)

        keras_y = converter.get_output_tensor(keras_layer)[0]
        converter.set_variable(keras_y, webdnn_y)

:func:`@KerasConverter.register_handler(typename)<webdnn.frontend.converter.Converter.register_handler>` is the decorator to register
handlers into converters. In convert phase, converter traverse model's computation graph from input to output. When :code:`typename`
layer is found, converter calls registered handler function with converter itself and found layer.

In handler function, there are 3 steps.

1. Get input WebDNN variables corresponding to input Keras variables.
2. Build graph structure.
3. Bind output WebDNN variable with the corresponding Keras variable.

.. image:: ./figures/keras_converter_internal.png
    :align: right

First, we get input WebDNN variable :code:`webdnn_x` from converter. Because converter traverses keras model from input to output,
:code:`keras_x` is already converted into WebDNN variable by the converter handler of previous layer. The converted WebDNN variables are
stored in the converter with corresponding keras tensor as key. We can get input WebDNN variables as follows:

.. code::

    keras_x = converter.get_input_tensor(keras_layer)[0]
    webdnn_x = converter.get_variable(keras_x)

:func:`converter.get_input_tensor(keras_layer)<webdnn.frontend.keras.KerasConverter.get_input_tensor>` returns the list of input
keras tensors of :code:`keras_layer`.

Next, we build WebDNN IR graph.

.. code::

    webdnn_operator = SquareOperator(None)
    webdnn_y, = webdnn_operator(webdnn_x)

The first argument of operator constructor is operator's name. If it is :code:`None`, name is automatically generated. When operator is
called, a tuple of output WebDNN variables is returned. **Don't forget to extract it (last comma of `webdnn_y,`).**

.. image:: ./figures/keras_converter_internal2.png
    :align: right

Finally, we register output WebDNN variables withs the corresponding keras tensors.
:func:`converter.get_output_tensor(keras_layer)<webdnn.frontend.keras.KerasConverter.get_output_tensor>` returns the list of
output keras tensors of `keras_layer`.

.. code::

    keras_y = converter.get_output_tensor(keras_layer)[0]
    converter.set_variable(keras_y, webdnn_y)

1.3. Define Generator Handler
-----------------------------

Generator Handler is function which generates runtime source code from IR. Luckily, implementing generator handler of elementwise
operation is very easy because you can use utility function
:func:`register_elementwise_kernel(OperatorClass, code)<webdnn.backend.webassembly.kernels.elementwise.register_elementwise_kernel>`.

.. code::

    from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel
    
    register_elementwise_kernel(SquareOperator, "y = x0 * x0;")

The first argument :code:`OperatorClass` is corresponding operator class, and the second argument :code:`code` is kernel code of each
elementwise operation. Because this utility function is for **webassembly backend**, :code:`code` is written in **C++**. :code:`x0` and
:code:`y` is pre-defined by this utility function.

Also, similar utility functions are defined in other backends.

.. code::

    from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_fallback
    from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webassembly
    from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webgpu

    register_elementwise_kernel_fallback(SquareOperator, "y = x0 * x0;")
    register_elementwise_kernel_webassembly(SquareOperator, "y = x0 * x0;")
    register_elementwise_kernel_webgpu(SquareOperator, "y = x0 * x0;")

That's all. Complete code is as follows.

.. code::

    # square.py

    import keras
    from webdnn.backend.fallback.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_fallback
    from webdnn.backend.webassembly.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webassembly
    from webdnn.backend.webgpu.kernels.elementwise import register_elementwise_kernel as register_elementwise_kernel_webgpu
    from webdnn.frontend.keras.converter import KerasConverter
    from webdnn.graph.operators.elementwise import Elementwise


    class SquareLayer(keras.layers.Layer):
        """
        calculate x^2 elementwisely
        """

        def call(self, x):
            return keras.backend.pow(x, 2)


    class SquareOperator(Elementwise):
        pass


    @KerasConverter.register_handler("SquareLayer")
    def square_converter_handler(converter: KerasConverter, keras_layer: SquareLayer):
        keras_x = converter.get_input_tensor(keras_layer)[0]
        webdnn_x = converter.get_variable(keras_x)

        webdnn_operator = SquareOperator(None)

        webdnn_y, = webdnn_operator(webdnn_x)
        keras_y = converter.get_output_tensor(keras_layer)[0]

        converter.set_variable(keras_y, webdnn_y)


    register_elementwise_kernel_fallback(SquareOperator, "y = x0 * x0;")
    register_elementwise_kernel_webassembly(SquareOperator, "y = x0 * x0;")
    register_elementwise_kernel_webgpu(SquareOperator, "y = x0 * x0;")

Test
----

Let's test the implementation.

.. code::

    # test.py

    import keras
    import square

    from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
    from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
    from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
    from webdnn.frontend.keras.converter import KerasConverter

    # Define Keras model
    x = keras.layers.Input((10,))
    y = square.SquareLayer()(x)
    model = keras.models.Model([x], [y])

    # Convert Keras model into WebDNN graph IR
    graph = KerasConverter(batch_size=1).convert(model)

    # Generate graph descriptors
    WebGPUDescriptorGenerator.generate(graph).save("./output")
    WebassemblyDescriptorGenerator.generate(graph).save("./output")
    FallbackDescriptorGenerator.generate(graph).save("./output")

.. code-block:: html

    <!--index.html-->

    <button onclick="main()">RUN</button>
    <script src="../../../dist/webdnn.js"></script>
    <script type="application/javascript">
        async function main() {
            let runner = await WebDNN.load("./output");
            let x = runner.getInputViews()[0];
            let y = runner.getOutputViews()[0];

            x.set([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);

            await runner.run();

            console.log(y.toActual());
        }
    </script>

The result is like follows.

.. image:: ./figures/section1_result.png

----

- :doc:`Next: "2. Elementwise Operator withs Parameters"<./section2>`
- :doc:`Prev: "0. Architecture of Graph Transpiler and How to Extend"<./section0>`
