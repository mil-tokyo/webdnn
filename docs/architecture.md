# Architecture overview

WebDNN v2 loads an ONNX model in the browser and runs inference on one of four
backends. This document describes the main layers and how they fit together.

## Layout

```
src/
  descriptor_runner/      # the runtime library shipped to the browser
    core/                 # model loading, graph execution, runner
    backend/              # backend implementations
      cpu/  wasm/  webgl/  webgpu/
    operators/            # operator (kernel) implementations, per backend
      base/  cpu/  wasm/  webgl/  webgpu/
    onnx/                 # ONNX parsing (protobufjs-generated bindings)
    interface/            # public TypeScript types / API surface
    image.ts  math.ts  util.ts  index.ts
  shader/
    webgpu/               # WGSL shader sources -> generated operator shaders
    wasm/                 # C++ kernels compiled to WebAssembly via emscripten
  graph_transpiler/       # Python offline model optimizer (package: webdnn)
scripts/                  # build / codegen scripts
test/                     # unit, fixtures, and E2E tests
```

## Runtime (`src/descriptor_runner`)

- **core** — entry point for `WebDNN.load(...)`. Parses the ONNX model, builds the
  execution graph, selects an available backend, and provides the `Runner` that
  executes the graph against input tensors.
- **backend** — backend-specific resource management (CPU, WebAssembly, WebGL,
  WebGPU). Backend selection falls back automatically (e.g. WebGPU → WebGL → CPU).
- **operators** — operator (kernel) implementations grouped by backend, with
  shared base classes under `operators/base`. Operator bundles are split out at
  build time and loaded dynamically at runtime (`dist/op-*.js`).
- **onnx** — protobufjs-generated bindings for the ONNX format
  (`onnx.js` / `onnx.d.ts`), regenerated with `npm run gen:onnx`.
- **interface** — the public type surface for library consumers.

## Shader / kernel generation (`src/shader`)

- **webgpu** — WGSL shader sources. `npm run shader:webgpu` (node) generates the
  WebGPU operator shaders consumed by `operators/webgpu`.
- **wasm** — C++ kernel sources compiled to WebAssembly with emscripten
  (`npm run shader:wasm`). Requires emscripten; not part of `build:all`. See
  [emscripten-setup.md](emscripten-setup.md).

In addition, `npm run makeShaderList` (`scripts/make_operator_entries.py`,
Python 3) generates the operator-entry tables used to register and dynamically
load operators.

## Build (`scripts/build.mjs`, Vite)

`npm run build:all` runs, in order:

1. `shader:webgpu` — generate WGSL operator shaders
2. `makeShaderList` — generate operator-entry tables (`opEntriesAll.ts`)
3. `build` — Vite build (`scripts/build.mjs`) producing 9 JS bundles
   (`webdnn.js`, `webdnn-core.js`, and `op-*.js`) plus `build:dts` (`dist/types/`)

`scripts/ensure-generated-stubs.mjs` writes placeholder stubs for generated files
so that `typecheck` / `build` work on a fresh clone before the real code
generation has run.

## Graph transpiler (`src/graph_transpiler`, Python)

The `webdnn` Python package is an offline graph optimizer. It takes an ONNX model
and produces an optimized representation that `dist/webdnn-core.js` can load
directly, avoiding in-browser optimization. Managed with uv / `pyproject.toml`.

## Testing

WebDNN uses a three-layer test strategy (unit, fixtures, browser E2E) described in
[testing.md](testing.md). Fixtures are generated with `npm run fixtures` (uv);
E2E runs through Playwright across CPU / WebGPU / WebGL.
