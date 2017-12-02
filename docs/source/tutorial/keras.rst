Use with Keras model
====================

In this tutorial, we'll convert ResNet50 [#f1]_ classification model pretrained in Keras [#f2]_ into WebDNN execution format.

1. Export Keras pretrained model
--------------------------------

.. code-block:: python

    from keras.applications import resnet50
    model = resnet50.ResNet50(include_top=True, weights='imagenet')
    model.save("resnet50.h5")

2. Convert Keras model to our computation graph format
------------------------------------------------------

.. code-block:: python

    python bin/convert_keras.py resnet50.h5 --input_shape '(1,224,224,3)' --out output

At least you need to specify the model file and the shape of input array.

Also you can convert via python script

.. code-block:: python

    from webdnn.frontend.keras import KerasConverter
    from webdnn.backend import generate_descriptor

    graph = KerasConverter(batch_size=1).convert(model)
    exec_info = generate_descriptor("webgpu", graph)  # also "webassembly", "webgl", "fallback" are available.
    exec_info.save("./output")

Now you have the "graph descriptor" to execute on the web browsers in output directory.

.. _js-api:

3. Run on web browser
---------------------

This document illustrates the essence of running the "graph descriptor" to execute on the web browsers.
In `convert_keras` example directory, the complete codes for training and converting a Keras model and running it on the web browsers can be found.

First, You have to initialize [`DescriptorRunner`](../api_reference/descriptor_runner/interfaces/webdnn.dnndescriptorrunner.html)
and load model data.

.. code-block:: js

    // ES6(modern JavaScript) version
    let runner = await WebDNN.load('./output');

    // traditional JavaScript version
    WebDNN.load('./output')
       .then(function(runner){
           console.log('loaded');

           // add your code here.
       });

WebDNN automatically select the best backend based on Browser type and
compiled model data on the server.

You can check the backend type

.. code-block:: js

    console.log(runner.backendName);

.. image:: ../_static/tutorial/check_backend.png

Then you can get input and output variable references (`SymbolicFloat32Array` type).

.. code-block:: js

    let x = runner.getInputViews()[0];
    let y = runner.getOutputViews()[0];

That's all for initialization. You only have to do this at once in the application.

Let's classify this image.

.. image:: ../_static/tutorial/sample_image2.jpeg

First, set input data. You can get image data as RGB format by using `WebDNN.Image sub module <../api_reference/descriptor-runner/modules/webdnn_image.html>`_

.. code-block:: js

    // ES6(modern JavaScript) version
    x.set(await WebDNN.Image.getImageArray('/example/data/school_bus.jpg', { dstW: 224, dstH: 224 }));

    // traditional JavaScript version
    WebDNN.Image.getImageArray('/example/data/school_bus.jpg', { dstW: 224, dstH: 224 })
       .then(function(array) {
           x.set(array);
       });

Next, run model.

.. code-block:: js

    // ES6(modern JavaScript) version
    await runner.run();

    // traditional JavaScript version
    runner.run()
       .then(function() {
           console.log('finished');
       });

That's all.

Show computed vector and predicted label.

.. code-block:: js

    let y_typed_array = y.toActual();
    console.log('Computed vector', y_typed_array);
    console.log('Predicted Label', WebDNN.Math.argmax(y_typed_array));

.. image:: ../_static/tutorial/result_keras.png

Congratulation! :code:`LabelID:779` is :code:`"School bus"` in ImageNet. It looks work well.

.. rubric:: References
.. [#f1] K. He, X. Zhang, S. Ren, and J. Sun, "Deep Residual Learning for Image Recognition", IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016.
.. [#f2] https://keras.io/applications/#resnet50
