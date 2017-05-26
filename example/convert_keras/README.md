# Keras model conversion example

## MNIST MLP model
### 1. Train model in Keras
```
python mnist_mlp.py
```

### 2. Convert model into WebDNN graph descriptor
```
python ../../bin/convert_keras.py output_mnist/keras_model/mnist_mlp.h5 --input_shape '(1,784)' --out output_mnist
```

The "input_shape" option is the shape of input array. First "1" is the batch size, and the following numbers are the shape of a sample.

### 3. Use in the web browser
You can now use the model on the web browser
[descriptor_run_mnist.html](http://localhost:8000/example/convert_keras/descriptor_run_mnist.html) via a HTTP server.


## MNIST Convolutional model
```
python mnist_mlp.py --model conv
```

Trains convolutional model.


### 2. Convert model into WebDNN graph descriptor
For conv model, the shape of input may be (1, 28, 28, 1) or (1, 1, 28, 28) depending on the training backend setting (data_format). You can check the shape when you run `mnist_mlp.py`.

```
$ python mnist_mlp.py --model conv
Using TensorFlow backend.
input shape: (28, 28, 1)
```

Depending on the backend setting, the suitable command for converting convolutional model is one of the follows.
```
python ../../bin/convert_keras.py output_mnist/keras_model/mnist_mlp.h5 --input_shape '(1,28,28,1)' --input_data_format channels_last --out output_mnist
python ../../bin/convert_keras.py output_mnist/keras_model/mnist_mlp.h5 --input_shape '(1,1,28,28)' --input_data_format channels_first --out output_mnist
```

### 3. Use in the web browser
You can now use the model on the web browser
[descriptor_run_mnist.html](http://localhost:8000/example/convert_keras/descriptor_run_mnist.html) via a HTTP server.
