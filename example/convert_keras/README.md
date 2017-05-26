# Keras model conversion example
Our scripts assume Keras version 2.0.x.

## MNIST MLP model
### 1. Train model in Keras
```sh
python mnist_mlp.py
```

### 2. Convert model into WebDNN graph descriptor
```sh
python ../../bin/convert_keras.py output_mnist/keras_model/mnist_mlp.h5 --input_shape '(1,784)' --out output_mnist
```

The "input_shape" option is the shape of input array. First "1" is the batch size, and the following numbers are the shape of a sample.

### 3. Use in the web browser
You can now use the model on the web browser
[descriptor_run_mnist.html](http://localhost:8000/example/convert_keras/descriptor_run_mnist.html) via a HTTP server.


## MNIST Convolutional model
```sh
python mnist_mlp.py --model conv
```

Trains convolutional model.


### 2. Convert model into WebDNN graph descriptor
For conv model, the shape of input is (1, 28, 28, 1) where (batchsize, h, w, channels). This order depends on the training backend setting (data_format). Currently, WebDNN converter supports only when `data_format==channels_last`.

```sh
python ../../bin/convert_keras.py output_mnist/keras_model/mnist_mlp.h5 --input_shape '(1,28,28,1)' --out output_mnist
```

### 3. Use in the web browser
You can now use the model on the web browser
[descriptor_run_mnist.html](http://localhost:8000/example/convert_keras/descriptor_run_mnist.html) via a HTTP server.

## ResNet-50 model
### 1. Exporting Keras sample model
In ipython, run the following statements.

```python
from keras.applications import resnet50
model = resnet50.ResNet50(include_top=True, weights='imagenet')
model.save("resnet50.h5")
```

### 2. Convert model into WebDNN graph descriptor
```sh
python ../../bin/convert_keras.py resnet50.h5 --input_shape '(1,224,224,3)' --out output
```

### 3. Use in the web browser
You can now use the model on the web browser
[descriptor_run_resnet.html](http://localhost:8000/example/convert_keras/descriptor_run_resnet.html) via a HTTP server.
