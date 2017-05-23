# MNIST model conversion sample
This example first trains MNIST classification model with Chainer, then transpiles it to WebDNN format (graph descriptor).

To run this example, you need to install Chainer.
```
pip install chainer
```

Train and convert MNIST classification model
```
python train_mnist.py
```

Then start a HTTP server on the package root directory (where `setup.py` exists)
```
python -m http.server
```

You can run the demo on `http://localhost:8000/example/mnist/descriptor_run_mnist.html`

For IE11, `http://localhost:8000/example/mnist/descriptor_run_mnist.es5.html`
