# MNIST model conversion sample
This directory contains examples of training MNIST classification model and transpiling it to WebDNN format (graph descriptor).

## Keras
Our scripts assume Keras version 2.0.x.

To run this example, you need to install Keras.

Train and convert MNIST classification model at once:
```
python train_mnist_keras.py --model fc
```

For `model` argument, `fc` (fully-connected) and `conv` (convolution) can be selected.

In fact, the script contains two steps:

1. Train model in Keras
    This is ordinary example of Keras. The model is saved to `output_keras/keras_model/mnist_mlp.h5`.

2. Executing converting command
    ```sh
    python ../../bin/convert_keras.py output_keras/keras_model/mnist_mlp.h5 --input_shape '(1,784)' --out output_keras
    ```

    The "input_shape" option is the shape of input array. First "1" is the batch size, and the following numbers are the shape of a sample.
    For convolution model, it changes to `(1,28,28,1)` where `(batchsize, height, width, channel)`. This order depends on the training backend setting (data_format). Currently, WebDNN converter supports only when `data_format==channels_last`.

## Tensorflow

To run this example, you need to install tensorflow. See [https://www.tensorflow.org/install/install_linux](https://www.tensorflow.org/install/install_linux).
```
pip install tensorflow
```

Train and convert MNIST classification model
```
python train_mnist_tensorflow.py
```

## Chainer

To run this example, you need to install Chainer.
```
pip install chainer
```

Train and convert MNIST classification model
```
python train_mnist_chainer.py
```

## Running on the web browser
Start a HTTP server on the package root directory (where `setup.py` exists)

```
python -m http.server
```

You can run the demo on `http://localhost:8000/example/mnist/descriptor_run_mnist.html`

For IE11, `http://localhost:8000/example/mnist/descriptor_run_mnist.es5.html`
