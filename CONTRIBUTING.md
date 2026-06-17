# How to contribute
We welcome contributions to WebDNN. This document describes the procedures and rules.

Kinds of contributions will be one of the following, but not restricted to:
- Bugfix
- Implementation of a layer
- Implementation of a converter from a deep learning framework
- Improvement of performance
- Documantation

# Development environment

- Node.js 20+ (see `.nvmrc`)
- Python 3.10+ via [uv](https://docs.astral.sh/uv/) (for the graph transpiler and test fixtures)
- emscripten 3.1+ (only for the WebAssembly backend; see [docs/emscripten-setup.md](docs/emscripten-setup.md))

Setup:

```
npm install
uv sync            # Python graph transpiler / fixtures
```

See [docs/architecture.md](docs/architecture.md) for a layer-by-layer overview of the codebase.

# Development workflow

```
npm run typecheck     # tsc --noEmit
npm run lint          # eslint
npm run format        # prettier --write   (format:check for CI)
npm test              # vitest (unit, no GPU)
npm run build:all     # WGSL gen + operator entries + Vite build + dts
```

Pre-commit gates (all must be green): `npm run typecheck`, `npm run lint`,
`npm run format:check`, `npm run test:unit`.

## Code generation

- **WGSL shaders** — after editing files under `src/shader/webgpu`, run `npm run shader:webgpu` to regenerate the WebGPU operator shaders.
- **WebAssembly kernels** — changes under `src/shader/wasm` require emscripten (see [docs/emscripten-setup.md](docs/emscripten-setup.md)). The WASM backend is not part of `npm run build:all`; distributing it requires updating `build:all` after emscripten is installed.
- **ONNX bindings** — regenerate the protobufjs bindings with `npm run gen:onnx`.

# Testing

If you add a feature, adding corresponding tests is recommended. WebDNN has a
three-layer test strategy described in [docs/testing.md](docs/testing.md).

```
npm test                          # unit tests (vitest)
npm run fixtures                  # generate ONNX test fixtures (uv)
npx playwright install chromium   # one-time, for E2E
npm run test:e2e                  # Playwright E2E (CPU / WebGPU / WebGL)
```

`npm run test:e2e` requires the fixtures (`npm run fixtures`) and the Playwright
Chromium browser to be installed.

# Pull Request
Send pull request from your fork branch to our master branch. The project organizer checks the request and accepts or gives request for revision.

# License
WebDNN is distributed under the MIT License. Every contributor holds the copyright of his/her part.

By contributing to the mil-tokyo/webdnn repository through pull-request, comment,
or otherwise, the contributor releases their content to the license and copyright
terms herein.

## Developer Certificate of Origin 1.1
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
