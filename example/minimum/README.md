# Minimum running example

A minimal sample of running an existing ONNX model using WebDNN.

This example runs `model/model.onnx`. This model contains only the `Relu` operator; the generation method is described in `make_model.py` (using PyTorch).

## Run on a web browser

At repository root, execute

```
yarn server
```

With this running, open [http://localhost:8080/example/minimum/](http://localhost:8080/example/minimum/) with a web browser.
