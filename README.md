# WebDNN

[日本語](README.ja.md)

WebDNN version 2 runs neural network inference directly in the web browser. The major difference from WebDNN 1.x is that WebDNN 2.x accepts ONNX models as input, allowing an ONNX model to be loaded straight into the browser without Python preprocessing. Offline model optimization is also available.

[Version 1.x](https://github.com/mil-tokyo/webdnn/tree/v1.2.11)

## Supported backends (acceleration technologies)

- **WebGPU** — current WGSL-based implementation. Works on modern Chrome / Edge (and on Safari / Firefox where WebGPU is enabled).
- **WebGL** — uses WebGL2 when available, with a WebGL1 fallback.
- **WebAssembly** — requires an emscripten build of the kernels. See [docs/emscripten-setup.md](docs/emscripten-setup.md).

## Environment

- Node.js 20+ (see `.nvmrc`)
- Python 3.10+ via [uv](https://docs.astral.sh/uv/) — only needed for model optimization and generating test fixtures
- emscripten 3.1+ — only needed to build the WebAssembly backend

## Setup

```
npm install
uv sync            # only if you use the Python graph transpiler / optimizer
```

## Build

```
npm run build:all
```

Build outputs (in `dist/`):

- `dist/webdnn.js` — UMD bundle (global `WebDNN`) that loads unoptimized ONNX models
- `dist/webdnn-core.js` — loads ONNX models optimized offline by WebDNN
- `dist/op-*.js` — operator bundles, loaded dynamically at runtime
- `dist/types/` — TypeScript type declarations

`build:all` runs WGSL shader generation (`shader:webgpu`) and operator-entry generation (`makeShaderList`, requires Python 3) before the Vite build. The WebAssembly backend is not built by `build:all`; building it requires emscripten (see [docs/emscripten-setup.md](docs/emscripten-setup.md)).

## Basic usage

Load `dist/webdnn.js` with a `<script>` tag to add a global `WebDNN` object. Assuming the ONNX model `model_directory/model.onnx` exists, run it with an input tensor of shape `[1, 2]`:

```javascript
const runner = await WebDNN.load("model_directory/");
const inputDataArray = new Float32Array([5.1, -2.3]);
const inputTensor = new WebDNN.CPUTensor([1, 2], "float32", inputDataArray);
const [outputTensor] = await runner.run([inputTensor]);

console.log(outputTensor.data); // Float32Array
```

See `example/minimum` for a complete minimal working example.

## Test

See [docs/testing.md](docs/testing.md) for the full testing guide.

```
npm test            # unit tests (vitest, no GPU required)
npm run fixtures    # generate ONNX test fixtures (uv, Python)
npm run test:e2e    # Playwright E2E (CPU / WebGPU / WebGL, automated)
npm run server      # static server for the manual browser runner
```

For the manual browser runner, open
<http://localhost:8080/test/model_test/runner/standard.html>, check the backend
you want to test, and click the Test button.

`npm run fixtures` generates the ONNX models and input/output tensors used by the
tests. (The legacy `test/model_test/make_models.py`, which depends on PyTorch,
remains only for large-model generation and is not part of the standard flow.)
