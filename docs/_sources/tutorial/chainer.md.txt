# Use with chainer model

```eval_rst
In this tutorial, we'll convert ResNet50 [#f1]_ classification model 
pretrained in Chainer [#f2]_ into WebDNN execution format.
```

1. Load chainer pretrained model

    ```python
    import chainer
 
    model = chainer.links.model.vision.resnet.ResNet50Layers()
    ```

2. Execute model with dummy data. In chainer, computation graph are defined by
    run. Therefore we need execute model at least once to construct the graph.

    ```python
    import numpy as np

    x = chainer.Variable(np.empty((1, 3, 224, 224), dtype=np.float32))
    y = model(x, layers=["fc6"])["fc6"]
    ```

3. Convert chainer computation graph to our computation graph format

    ```python
    from webdnn.frontend.chainer import ChainerGraphConverter

    graph = ChainerGraphConverter().convert_from_inout_vars([x], [y])
    ```

4. Generate and save execution information.

    ```python
    from webdnn.backend.interface.generator import generate_descriptor

    exec_info = generate_descriptor("webgpu", graph)
    exec_info.save("./output")
    ```

```eval_rst
.. rubric:: References
.. [#f1] K. He, X. Zhang, S. Ren, and J. Sun, "Deep Residual Learning for Image Recognition", IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016.
.. [#f2] http://docs.chainer.org/en/latest/reference/links.html#chainer.links.ResNet50Layers
```
