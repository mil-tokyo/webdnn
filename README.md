# WebDNN

[日本語](README.ja.md)

This is the alpha version of WebDNN version 2. The main difference between WebDNN 1.x and WebDNN 2.x is that WebDNN 2.x only accepts ONNX models as input, allowing ONNX models to be loaded directly into a web browser without Python preprocessing. In addition, offline model optimization is also possible.

[Version 1.x](https://github.com/mil-tokyo/webdnn/tree/v1.2.11)

# Supported backends (acceleration technologies)

WebGL is available in most modern browsers.

- WebGPU
  - The draft version implemented in Chrome Canary.
  - The WebGPU in iOS13 is not supported because it requires shaders based on the deprecated WSL language.
- WebGL
  - Use WebGL2 if available; also supports Safari, which only supports WebGL1.
- WebAssembly

# Environment setting

The environment which runs node.js 14, python 3.6+ and emscripten 2.0+.

```
yarn
python setup.py develop
```

# Build
```
yarn build:all
```

Build outputs:
- `dist/webdnn.js`
  - Library that can load unoptimized ONNX models
- `dist/webdnn-core.js`
  - Library that can load optimized ONNX models by WebDNN

# Basic usage

Load `dist/webdnn.js` with the `<script>` tag to globally add a `WebDNN` object. Assuming that the ONNX model `model_directory/model.onnx` exists, and run the model with a input tensor of the shape `[1, 2]`.

```javascript
const runner = await WebDNN.load("model_directory/");
const inputDataArray = new Float32Array([5.1, -2.3]);
const inputTensor = new WebDNN.CPUTensor([1, 2], "float32", inputDataArray);
const [outputTensor] = await runner.run([inputTensor]);

console.log(outputTensor.data);  // Float32Array
```

See `example/minimum` for the complete minimal code that works.

# Test

Generate ONNX models and input/output tensors to be tested

```
python test/model_test/make_models.py
```

Run on web browser

```
yarn server
```

Open <http://localhost:8080/test/model_test/runner/standard.html> with web browser, check the backend you want to test, and click the Test button to run the test.

Use

```
python test/model_test/make_models.py --optimize
```

<http://localhost:8080/test/model_test/runner/optimized.html>

when testing, including model optimization. However, the execution time of `make_models.py` takes a long time.
