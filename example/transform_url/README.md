# Transforming URL example
WebDNN's model files are relatively large, so website developers may want to load them from another server.

In this example, mnist model is loaded from another server, specified in the form.

The core of this example is `transformUrlDelegate` function in `script.js`.

# Setup
HTTP server with CORS header is needed to run the example. You may install it with `npm install -g http-server`.

You need to run mnist example in advance.

```bash
# start at webdnn root directory
$ cd example/mnist
$ python train_mnist_chainer.py  # another framework is ok
$ cd ../..
$ http-server -p 8000
```

Then open `http://localhost:8000/example/mnist/` and check if it works.

# Run
Run another http server to serve webdnn model files.

```bash
# start at webdnn root directory
$ cd example/mnist/output_chainer  # directory depends on which framework you used
$ http-server -p 8001 --cors  # "cors" is needed
```

Then open `http://localhost:8000/example/transform_url/` and check if it works.

See the browser's console and server log to investigate which file is loaded from which server.
