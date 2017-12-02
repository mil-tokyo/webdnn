frontend
========

Module :code:`webdnn.frontend` contains model converters for other DNN frameworks.

.. toctree::
    :hidden:
    :maxdepth: 1

    ./chainer
    ./converter
    ./keras
    ./onnx
    ./pytorch
    ./tensorflow

- :doc:`webdnn.frontend.chainer.ChainerConverter<./chainer>`

    Model converter for `Chainer <https://chainer.org/>`_

- :doc:`webdnn.frontend.converter.Converter<./converter>`

    Model converter base class

- :doc:`webdnn.frontend.keras.KerasConverter<./keras>`

    Model converter for `Keras <https://keras.io>`_

- :doc:`webdnn.frontend.onnx.ONNXConverter<./onnx>`

    Model converter for `Open Neural Network Exchange (ONNX) <http://onnx.ai/>`_

- :doc:`webdnn.frontend.pytorch.PyTorchConverter<./pytorch>`

    Model converter for `PyTorch <http://pytorch.org/>`_

- :doc:`webdnn.frontend.tensorflow.TensorFlowConverter<./tensorflow>`

    Model converter for `TensorFlow <https://www.tensorflow.org/>`_
