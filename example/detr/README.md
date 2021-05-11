# Object detection using DETR

PyTorch (`>=1.7`) is required to run the Python script.

# Operation procedure
## Convert PyTorch model into ONNX model
```
python conversion.py
```

## Run on a web browser

At repository root, execute

```
yarn server
```

With this running, open [http://localhost:8080/example/detr/](http://localhost:8080/example/detr/) with a web browser.
