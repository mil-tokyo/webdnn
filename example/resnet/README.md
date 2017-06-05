# ResNet-50 model conversion example
This example converts pre-trained ResNet-50 image classification model of Keras or Chainer into WebDNN format (graph descriptor).

## Model conversion (Keras)
Our scripts assume Keras version 2.0.x.

`convert_resnet_keras.py` does all things at once.

The script consists of two parts:

1. Exporting Keras sample model
    In python, run the following statements.

    ```python
    from keras.applications import resnet50
    model = resnet50.ResNet50(include_top=True, weights='imagenet')
    model.save("resnet50.h5")
    ```

2. Convert model into WebDNN graph descriptor
    ```sh
    python ../../bin/convert_keras.py resnet50.h5 --input_shape '(1,224,224,3)' --out output_keras
    ```

## Model conversion (Chainer)
You can convert the model with `convert_resnet_chainer.py`.

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
