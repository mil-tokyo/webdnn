# Caffe model conversion example
This example converts a model trained by Caffe into WebDNN format (graph transpiler).

## Model conversion
See `caffenet_conversion.ipynb`. Can be viewed online [https://github.com/mil-tokyo/webdnn/blob/master/example/convert_caffe/caffenet_conversion.ipynb](https://github.com/mil-tokyo/webdnn/blob/master/example/convert_caffe/caffenet_conversion.ipynb)

## Running on the web browser
Start a HTTP server on the package root directory (where `setup.py` exists)
```
python -m http.server
```

You can run the demo on `http://localhost:8000/example/convert_caffe/descriptor_run_caffenet.html`
