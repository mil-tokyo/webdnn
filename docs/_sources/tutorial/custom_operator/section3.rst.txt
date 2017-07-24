3. Layer with Weights
=====================

.. toctree::
    :maxdepth: 1

In this section, you will learn about how to convert **custom keras layer which has trainable weights**.
 
Complete sample code is included in :code:`/example/custom_operator/section3`.

Example: Bias
-------------

In :doc:`section 1<./section1>` and :doc:`section 2<./section2>`, we learned how to convert operators which have no weights.

In this section, we'll consider :code:`BiasLayer` defined as follows:

.. code::

    class BiasLayer(keras.layers.Layer):
        """
        Trainable bias layer

        # Input shape
            2D tensor of shape `(num_samples, features)`.

        # Output shape
            2D tensor of shape `(num_samples, features)`.
        """

        def build(self, input_shape):
            self.bias = self.add_weight(name='bias',
                                        shape=(input_shape[-1],),
                                        initializer=keras.initializers.get("uniform"))

        def call(self, x):
            return x + self.bias

This layer has a trainable weight named :code:`"bias"`.


Axis and Order
--------------

To define variables and operations' semantics, :class:`~webdnn.Axis` and :class:`~webdnn.Order` object is defined in WebDNN.

Axis
^^^^

:class:`~webdnn.Axis` object represents each dimension of tensors. Typical axes are pre-defined like follows:

.. code::

    Axis.N  # batch size
    Axis.C  # number of features
    Axis.H  # height of image
    Axis.W  # width of image
    Axis.T  # length of series

For example, a tensor of shape :code:`(batch_size, features)` is 2D tensor. This tensor's first dimension is represented as
:obj:`Axis.N<webdnn.Axis.N>`, and second dimension is represented as :obj:`Axis.C<webdnn.Axis.C>` in WebDNN.

Also, :class:`~webdnn.Axis` object is used to define operation. For example :class:`~webdnn.graph.operators.softmax.Softmax`
operator is compute normalized exponential values. Generally, that values are normalized along to :obj:`Axis.C<webdnn.Axis.C>`.

Order
^^^^^

:class:`~webdnn.Order` object represents the data order of variables. For example, the data order of a tensor of shape
:code:`(batch_size, features)` is :obj:`~webdnn.graph.orders.OrderNC`.

WebDNN operators are designed to receive various data order. For example, generally
:class:`~webdnn.graph.operators.softmax.Softmax` operator is used to normalize :obj:`~webdnn.graph.orders.OrderNC` variable
along to :obj:`Axis.C<webdnn.Axis.C>` and the output is also :obj:`~webdnn.graph.orders.OrderNC` variable. However WebDNN
:class:`~webdnn.graph.operators.softmax.Softmax` operator can receives :obj:`~webdnn.graph.orders.OrderCN` variable too.

Typical order is defined in :mod:`webdnn.graph.order`.

Define Converter Handler
------------------------

Based on previous section, Let's convert :code:`BiasLayer`.
Luckily, bias operator is already implemented in webdnn as :code:`ElementwiseAdd`, or operator :code:`+`. You only have to implement
converter handler. Converter handler is implemented like follows:

.. code::

    from webdnn.frontend.keras.converter import KerasConverter

    @KerasConverter.register_handler("BiasLayer")
    def square_converter_handler(converter, keras_layer):
        keras_x = converter.get_input_tensor(keras_layer)[0]
        webdnn_x = converter.get_variable(keras_x)

        webdnn_b = converter.convert_to_constant_variable(keras_layer.bias, OrderC)

        webdnn_y = webdnn_x + webdnn_b
        keras_y = converter.get_output_tensor(keras_layer)[0]

        converter.set_variable(keras_y, webdnn_y)

The important lines are follows:

.. code::

    webdnn_b = converter.convert_to_constant_variable(keras_layer.bias, OrderC)

:func:`converter.convert_to_constant_variable(weight, order)<webdnn.frontend.keras.KerasConverter.convert_to_constant_variable>` is the
function which converts keras weights into WebDNN variables. The output variables' data order is determined by :code:`order`. In
:code:`BiasLayer`'s case, :code:`bias` is a tensor of shape :code:`(features,)`. Therefore :code:`order=OrderC` is specified.

Different from :code:`webdnn_x` and :code:`webdnn_y`, it's not need to store :code:`webdnn_b` into converter because
:code:`keras_layer.bias` is not referenced from other keras layers.


Test
----

Let's test the implementation.

.. code::

    # test.py

    import bias
    import keras
    import numpy as np
    from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
    from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
    from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
    from webdnn.frontend.keras.converter import KerasConverter

    # Define Keras model
    x = keras.layers.Input((10,))
    layer = bias.BiasLayer()
    y = layer(x)
    model = keras.models.Model([x], [y])

    # For test, initialize bias by 100.
    keras.backend.set_value(layer.bias, np.ones(layer.bias.shape) * 100)

    # Convert Keras model into WebDNN graph IR
    graph = KerasConverter(batch_size=1).convert(model)

    # Generate graph descriptor
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

.. image:: ./figures/section3_result.png

----

- :doc:`Prev: "2. Elementwise Operator with Parameters"<./section2>`
