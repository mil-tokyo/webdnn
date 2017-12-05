Use with PyTorch model
======================

In this tutorial, we'll convert AlexNet [#f1]_ pretrained in PyTorch [#f2]_ into WebDNN execution format.

1. Load PyTorch pretrained model

.. code-block:: python

    import torch, torchvision
    from webdnn.frontend.pytorch import PyTorchConverter

    model = torchvision.models.alexnet(pretrained=True)

    graph = PyTorchConverter().convert(model, dummy_input)

2. Prepare dummy input to construct computation graph

.. code-block:: python

    dummy_input = torch.autograd.Variable(torch.randn(1, 3, 224, 224))

3. Convert to WebDNN graph

.. code-block:: python

    graph = PyTorchConverter().convert(model, dummy_input)

4. Generate and save execution information.

.. code-block:: python

    from webdnn.backend import generate_descriptor

    exec_info = generate_descriptor("webgpu", graph)  # also "webassembly", "webgl", "fallback" are available.
    exec_info.save("./output")

To run converted model on web browser, please see :ref:`"#3. Run on web browser" in keras tutorial<js-api>`

.. rubric:: References
.. [#f1] Krizhevsky, Alex, Ilya Sutskever, and Geoffrey E. Hinton. "ImageNet Classification with Deep Convolutional Neural Networks." Advances in neural information processing systems. 2012.
.. [#f2] https://pytorch.org
