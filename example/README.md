# WebDNN examples
This directory contains some examples to illustrate typical usage of WebDNN.

## Common setup
Before running these examples, you have to install `webdnn` python library and start a HTTP server on the repository root directory.

You can run a HTTP server with standard python feature.

```
python -m http.server
```

## MNIST training and conversion
`mnist` directory contains the example to train and convert a DNN for classifying the MNIST dataset.

This example illustrates how to use Keras and Chainer model for WebDNN.

## ResNet-50 model conversion
`resnet` directory contains the example to convert the pre-trained ResNet-50 large-scale image classification DNN for WebDNN.

This example illustrates how to use Keras and Chainer model for WebDNN.

## Caffe model conversion
`convert_caffe` directory contains the example to convert the CaffeNet large-scale DNN for WebDNN.

This example illustrates how to use Caffe model for WebDNN.

## Neural Style Transfer
`convert_neural_style_transfer` directory contains the example to convert the [Neural Style Transfer model](https://github.com/gafr/chainer-fast-neuralstyle-models) for WebDNN.

This is intended to be example of interactive application.

## Benchmark
`benchmark` directory contains the speed benchmark to compare WebDNN and Keras.js.
