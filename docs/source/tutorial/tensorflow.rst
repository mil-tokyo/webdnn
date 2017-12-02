Use with TensorFlow model
=========================

In this tutorial, we'll convert model in TensorFlow [#f1]_ into WebDNN execution format.


1. Construct TensorFlow computation graph

.. code-block:: python

    import tensorflow as tf

    # y = x @ W + b
    x = tf.placeholder(tf.float32, [None, 784])
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))
    y = tf.nn.softmax(tf.matmul(x, W) + b)

2. Convert to WebDNN graph

.. code-block:: python

    from webdnn.frontend.tensorflow import TensorFlowConverter
    graph = TensorFlowConverter().convert([x], [y])

4. Generate and save execution information.

.. code-block:: python

    from webdnn.backend import generate_descriptor

    exec_info = generate_descriptor("webgpu", graph)  # also "webassembly", "webgl", "fallback" are available.
    exec_info.save("./output")

To run converted model on web browser, please see :ref:`"#3. Run on web browser" in keras tutorial<js-api>`

.. rubric:: References
.. [#f1] https://www.tensorflow.org
