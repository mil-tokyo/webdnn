# Keras model conversion example

## MNIST MLP model
Train model in Keras first:
```
python mnist_mlp.py
```

Then, convert to WebDNN graph descriptor:
```
python ../../bin/convert_keras.py output_mnist/keras_model/mnist_mlp.h5 --input_shape '(1,784)' --out output_mnist
```

You can now use the model on the web browser: open [descriptor_run_mnist.html](http://localhost:8000/example/convert_keras/descriptor_run_mnist.html) via a HTTP server.
