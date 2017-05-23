# ResNet-50 model conversion example
This example converts pre-trained ResNet-50 image classification model of Chainer into WebDNN format (graph descriptor).

## Model conversion
You can convert the model with `convert.py`.

```
python convert.py --model resnet50 --backend webgpu --encoding eightbit
```

- model can be either vgg16 and resnet50.
- backend can be webgpu, webassembly, fallback.
- encoding is optional argument, `--encoding eightbit` compresses the model weight into about 1/5 size (using approximation).

## Running on the web browser
Start a HTTP server on the package root directory (where `setup.py` exists)
```
python -m http.server
```

You can run the demo on `http://localhost:8000/example/convert_resnet/descriptor_run_resnet.html`

For IE11, `http://localhost:8000/example/convert_resnet/descriptor_run_resnet.es5.html`
 can be used. This is also example of automatic conversion of user code to ES5-compliant JavaScript code (see tips/es5).
