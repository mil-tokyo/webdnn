# Example of custom operator implementation

A sample that implements and runs a custom operator that does not exist in the ONNX specification.

Create a model that contains a custom operator named `Twice` that doubles the input and run it on WebDNN.

PyTorch (`>=1.7`) is required to run the Python script.

# Operation procedure
## Generate ONNX models with custom operators
```
python make_model.py
```

## Install custom operator implementation

Copy `twice.ts`, the implementation of the custom operator, to `<repository_root>/src\descriptor_runner\operators\cpu\operators\custom\twice.ts`.

## Build an operator set with custom operators

```
python -m webdnn.optimize_model output/model.onnx output
```

Output files `model-{cpu,wasm,webgl}.onnx`, `op-{cpu,wasm,webgl}.js`, `weight-{cpu,wasm,webgl}-0.bin` are generated. `op-{cpu,wasm,webgl}.js` includes standard and custom operator implementations.`model.onnx` is no longer needed.

## Run on a web browser

At repository root, execute

```
yarn server
```

With this running, open [http://localhost:8080/example/custom_operator/](http://localhost:8080/example/custom_operator/) with a web browser.

In this sample, the custom operator is an implementation running on the CPU; the standard operator, for which there is an implementation running on the GPU, runs on the GPU, and tensor data is automatically transferred between the CPU and GPU before and after the custom operator is executed.
