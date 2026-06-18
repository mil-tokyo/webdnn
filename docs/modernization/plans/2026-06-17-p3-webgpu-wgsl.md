# WebDNN 刷新 — Phase 3: WebGPU WGSL 移行 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 廃止された GLSL+SPIR-V(glslang) 経路を現行 WebGPU 規格（WGSL + 現行 API）へ全面移行し、最新ブラウザで WebGPU 推論を復活させる。

**Architecture:** 12 個の GLSL コンピュートシェーダを WGSL へ書き換え、`compile.js` を「`.wgsl` を文字列として `shaders.ts` に埋め込む」生成器に刷新する。`webgpuContextImpl.ts` の旧 API（`@ts-expect-error` 済み 4 箇所）を現行化し、`createPipeline` はシェーダを WGSL 文字列で受け取る。`@webgpu/glslang` を除去し、`shader:webgpu` を `build:all` に戻す。検証は P2 の Playwright/目視ランナーで、可能なら開発機の WebGPU 対応ブラウザを使って数値一致を自動確認し、最終的な実 GPU 確認は人手で行う。

**Tech Stack:** WGSL, 現行 WebGPU API（`@webgpu/types@0.1.70`）, Node 生成スクリプト, P2 の Playwright/vitest/uv フィクスチャ。

**上位計画:** [docs/modernization-plan.md](../modernization-plan.md) Phase 3。前提（P1 ツールチェーン・P2 テスト基盤）は完了済み。

**スコープ確定事項:**
- WebGPU バックエンドが対応する ONNX op は **Relu / Add / Gemm / Conv** の 4 種（operator ファイル: `unary.ts` / `binary7.ts` / `gemm.ts` / `conv.ts`）。
- シェーダ 12 本: `relu`, `binary_elementwise_add`, `binary_broadcast_add_{0,1,2,3,4}d`, `gemm`, `conv_im2col`, `conv_matmul`, `conv_bias`, `conv_transpose`。
- 演算子側（meta レイアウト・workGroups 計算・`createPipeline(name, webgpuShaders[name], nBuffers)` 呼び出し）は **変更しない**。WGSL 側を現行の meta/バインディング契約に合わせる。

**重要な前提（実行者向け）:**
- WebGPU の数値正当性の最終確認には**実 GPU が必要**。CI では実行しない。開発機（macOS/Apple Silicon 等）の Chrome/Chromium は Dawn/Metal 経由で WebGPU を実行できる場合があり、その場合は Playwright で自動検証できる。できない場合は人手の目視確認に委ねる（status の「人手が必要」）。
- WGSL の**コンパイルエラー**は GPU 無しでも `device.createShaderModule` が必要なため完全な静的検証は難しいが、WebGPU 対応ブラウザ上で `createShaderModule` の `compilationInfo()` によりエラー検出できる。Task 9 の検証で用いる。
- 各タスクは P1/P2 のゲート（`typecheck`/`lint`/`format:check`/`test:unit`/`build`）を緑に保つこと。

---

## GLSL → WGSL 翻訳ガイド（全シェーダ共通）

現行シェーダは全て次の構造を持つ:
- `layout(local_size_x = 64, ...) in;` → WGSL: `@compute @workgroup_size(64, 1, 1)`
- データバッファ `layout(std430, set=0, binding=N) [readonly] buffer X { float numbers[]; } x;`
  → WGSL: `@group(0) @binding(N) var<storage, read_write> x: array<f32>;`
  （**注意**: 現行の `createPipeline` は全バインディングを `buffer: { type: "storage" }`（= read_write）でレイアウト宣言する。レイアウトを変えないため、入力バッファも含め WGSL は全て `read_write` で宣言する。`read` 宣言にするとレイアウト不一致になるので使わない。）
- Meta バッファ `layout(std430, set=0, binding=M) readonly buffer Meta { uint a; uint b; ... } meta;`
  → WGSL: `struct Meta { a: u32, b: u32, ... }` + `@group(0) @binding(M) var<storage, read_write> meta: Meta;`
  （meta も storage バッファとして渡される。`int`→`i32`、`uint`→`u32`、`float`→`f32`。フィールド順・型は GLSL と完全一致させる。std430 では連続する同型スカラは 4byte 連続で、JS 側 `WebGPUMetaBuffer` も 4byte ずつ連続書き込みなので、スカラのみの Meta は順番どおりでアラインメント問題なし。）
- `gl_GlobalInvocationID.x` → `@builtin(global_invocation_id) global_id: vec3<u32>` を `main` 引数に取り、`global_id.x`。
- グリッドストライドループ `for (uint i = gl_GlobalInvocationID.x; i < len; i += 4096)`
  → `for (var i = global_id.x; i < len; i = i + 4096u) { ... }`
- 整数リテラルは型注釈に注意（`u32` には `4096u`、`i32` には `4096`)。`x % y`, `x / y` は WGSL でも整数同士なら整数演算。
- 配列インデックスは `x.numbers[i]` → `x[i]`（WGSL の array 変数名直下）。
- entryPoint は `main`（`@compute fn main(...)`）。

**完全な対応例 1（最小）— `relu`:**
GLSL:
```glsl
#version 450
layout(local_size_x = 64, local_size_y = 1, local_size_z = 1) in;
layout(std430, set = 0, binding = 0) readonly buffer arrayX { float numbers[]; } array_x;
layout(std430, set = 0, binding = 1) buffer arrayY { float numbers[]; } array_y;
layout(std430, set = 0, binding = 2) readonly buffer Meta { uint len; } meta;
void main() {
  uint len = meta.len;
  for (uint i = gl_GlobalInvocationID.x; i < len; i += 4096) {
    array_y.numbers[i] = max(array_x.numbers[i], 0.0);
  }
}
```
WGSL（`relu.wgsl`）:
```wgsl
struct Meta { len: u32, };
@group(0) @binding(0) var<storage, read_write> array_x: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_y: array<f32>;
@group(0) @binding(2) var<storage, read_write> meta: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let len = meta.len;
  for (var i = global_id.x; i < len; i = i + 4096u) {
    array_y[i] = max(array_x[i], 0.0);
  }
}
```
（注: 実際の `relu.glsl` の中身は本タスク着手時に必ず原本を確認し、上の例と差異があれば原本に忠実に訳すこと。）

**完全な対応例 2（ブロードキャスト）— `binary_broadcast_add_2d`:**
GLSL Meta は `{ uint len; uint outShape0, outShape1; uint inAStride0, inAStride1; uint inBStride0, inBStride1; }`、本体はインデックス分解して加算。WGSL:
```wgsl
struct Meta {
  len: u32,
  outShape0: u32, outShape1: u32,
  inAStride0: u32, inAStride1: u32,
  inBStride0: u32, inBStride1: u32,
};
@group(0) @binding(0) var<storage, read_write> array_a: array<f32>;
@group(0) @binding(1) var<storage, read_write> array_b: array<f32>;
@group(0) @binding(2) var<storage, read_write> array_c: array<f32>;
@group(0) @binding(3) var<storage, read_write> meta: Meta;

@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
  let len = meta.len;
  for (var i = global_id.x; i < len; i = i + 4096u) {
    let dim1 = i % meta.outShape1;
    let dim0 = i / meta.outShape1;
    array_c[i] = array_a[dim0 * meta.inAStride0 + dim1 * meta.inAStride1]
               + array_b[dim0 * meta.inBStride0 + dim1 * meta.inBStride1];
  }
}
```
（各 `_Nd` 版は次元数だけ異なる。原本の index 分解ロジックに忠実に訳すこと。）

---

## ファイル構成

**作成:**
- `src/shader/webgpu/shadersources/standard/*.wgsl` — 12 本（既存 `.glsl` を置換する新ソース）
- 検証用 WebGPU フィクスチャ（Task 8 で `test/fixtures/generate_fixtures.py` に gemm/conv 追加）

**変更:**
- `src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts` — `createPipeline` を WGSL string 化、`compute`/`dispatchWorkgroups`/`end` へ、`@ts-expect-error` 4 箇所除去
- `src/shader/webgpu/compile.js` — glslang 廃止、`.wgsl` を読んで `Record<string,string>` を出力
- `scripts/ensure-generated-stubs.mjs` — `shaders.ts` スタブ型を `Record<string, string>` に
- `package.json` — `@webgpu/glslang` 除去、`build:all` に `shader:webgpu` 復帰
- `test/fixtures/generate_fixtures.py` — gemm/conv フィクスチャ追加（Task 8）

**削除:**
- `src/shader/webgpu/shadersources/standard/*.glsl`（12 本、WGSL 化後）

---

## Task 1: WebGPU コンテキスト API の現行化

**Files:**
- Modify: `src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts`

旧 API を現行化し、`@ts-expect-error`（4 箇所）を除去する。`createPipeline` のシェーダ引数を `Uint32Array` から `string`(WGSL) に変える。

- [ ] **Step 1: `createPipeline` のシグネチャと中身を更新**

現状（抜粋）:
```typescript
  createPipeline(name: string, shader: Uint32Array, nBuffers: number): void {
    ...
      // TODO(P3): ... // @ts-expect-error ...
      shaderModule = device.createShaderModule({ code: shader }),
      pipeline = device.createComputePipeline({
        layout: pipelineLayout,
        // TODO(P3): ... // @ts-expect-error ...
        computeStage: {
          module: shaderModule,
          entryPoint: "main",
        },
      });
```
↓ 置換:
```typescript
  createPipeline(name: string, shader: string, nBuffers: number): void {
    ...
      shaderModule = device.createShaderModule({ code: shader }),
      pipeline = device.createComputePipeline({
        layout: pipelineLayout,
        compute: {
          module: shaderModule,
          entryPoint: "main",
        },
      });
```
（`bindings`/`bindGroupLayout`/`pipelineLayout` 部分は変更しない。2 つの `// TODO(P3)` + `// @ts-expect-error` コメント行を削除する。）

- [ ] **Step 2: `run()` の dispatch / endPass を更新**

現状（抜粋）:
```typescript
    // TODO(P3): rename to dispatchWorkgroups (current WebGPU API)
    // @ts-expect-error legacy WebGPU API; rewritten in Phase 3
    passEncoder.dispatch(
      request.workGroups.x,
      request.workGroups.y,
      request.workGroups.z
    );
    ...
    // TODO(P3): rename to end() (current WebGPU API)
    // @ts-expect-error legacy WebGPU API; rewritten in Phase 3
    passEncoder.endPass();
```
↓ 置換（コメント 2 行ずつ削除し、API 名を変更）:
```typescript
    passEncoder.dispatchWorkgroups(
      request.workGroups.x,
      request.workGroups.y,
      request.workGroups.z
    );
    ...
    passEncoder.end();
```

- [ ] **Step 3: 残存する @ts-expect-error が無いことを確認**

Run:
```bash
grep -n "@ts-expect-error\|TODO(P3)" src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts || echo "none (OK)"
```
Expected: `none (OK)`。

- [ ] **Step 4: 型チェック**

この時点では `createPipeline` 呼び出し側（operators）が `webgpuShaders[name]`（現状 `Uint32Array`）を渡すため、`shader: string` と不一致になり型エラーが出る。これは Task 3 で `shaders.ts` を `Record<string,string>` 化すると解消する。**本タスク単独では typecheck が webgpu operators で赤くなる**ことを許容し、次のように確認する:
```bash
npx tsc --noEmit -p tsconfig.json 2>&1 | grep -E "operators/webgpu|shaders" | head
```
Expected: `webgpuShaders[...]` 由来の型不一致のみ（`backend/webgpu/webgpuContextImpl.ts` 内のエラーは 0）。他の場所にエラーが波及していないこと。

- [ ] **Step 5: コミット**

```bash
git add src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts
git commit -m "feat(webgpu): modernize API (compute/dispatchWorkgroups/end), WGSL string shaders"
```
（注: この時点で `npm run typecheck` は webgpu operators で赤い。Task 3 完了で緑に戻る。Task 1〜3 は一連で完了させること。）

---

## Task 2: シェーダ生成パイプラインを WGSL 化

**Files:**
- Modify: `src/shader/webgpu/compile.js`
- Modify: `scripts/ensure-generated-stubs.mjs`

- [ ] **Step 1: `compile.js` を WGSL 文字列埋め込みに書き換え**

現状は `@webgpu/glslang` で `.glsl`→SPIR-V(Uint32Array)。これを `.wgsl` を読んで文字列として埋め込む形へ:

`src/shader/webgpu/compile.js` 全体を置換:
```javascript
// Compile WGSL shader sources into a single TypeScript module.
// Reads src/shader/webgpu/shadersources/standard/*.wgsl and emits
// src/descriptor_runner/operators/webgpu/shaders.ts as Record<string, string>.
const fs = require("fs");
const path = require("path");

const sourcesDir = path.join(__dirname, "shadersources", "standard");
const outPath = path.join(
  __dirname,
  "..",
  "..",
  "descriptor_runner",
  "operators",
  "webgpu",
  "shaders.ts"
);

let out = "/* eslint-disable */\n";
out += "// auto-generated by src/shader/webgpu/compile.js from *.wgsl sources\n";
out += "export const webgpuShaders: Record<string, string> = {\n";

for (const file of fs.readdirSync(sourcesDir).sort()) {
  if (!file.endsWith(".wgsl")) continue;
  const name = file.replace(/\.wgsl$/, "");
  const src = fs.readFileSync(path.join(sourcesDir, file), "utf-8");
  // Embed as a JSON-escaped string literal (safe for backticks/backslashes).
  out += `  ${JSON.stringify(name)}: ${JSON.stringify(src)},\n`;
}

out += "};\n";
fs.writeFileSync(outPath, out);
console.log("wrote", outPath);
```

- [ ] **Step 2: スタブ生成器の `shaders.ts` 型を更新**

`scripts/ensure-generated-stubs.mjs` の shaders.ts スタブ内容（現状 `Record<string, Uint32Array>`）を WGSL 用に変更:
```javascript
  {
    path: "src/descriptor_runner/operators/webgpu/shaders.ts",
    content:
      "/* eslint-disable */\n" +
      "// STUB: real file is generated by `npm run shader:webgpu` from *.wgsl. See Phase 3.\n" +
      "export const webgpuShaders: Record<string, string> = {};\n",
  },
```

- [ ] **Step 3: コミット**

```bash
git add src/shader/webgpu/compile.js scripts/ensure-generated-stubs.mjs
git commit -m "build(webgpu): emit WGSL strings from compile.js; update stub type"
```

---

## Task 3: WGSL シェーダの作成（relu / binary 系 6 本）

**Files:**
- Create: `src/shader/webgpu/shadersources/standard/{relu,binary_elementwise_add,binary_broadcast_add_0d,binary_broadcast_add_1d,binary_broadcast_add_2d,binary_broadcast_add_3d,binary_broadcast_add_4d}.wgsl`
- Reference (read, then delete in Task 5): 対応する `.glsl`

各 `.wgsl` は、対応する `.glsl` 原本を読み、翻訳ガイドに従って訳す。バインディング番号・Meta フィールド順・本体ロジックは原本に忠実に。`relu` と `binary_broadcast_add_2d` は本計画上部の完全例を使用してよいが、**必ず原本と突き合わせて差異がないか確認**すること。

- [ ] **Step 1: 各 `.glsl` 原本を確認**

Run:
```bash
for f in relu binary_elementwise_add binary_broadcast_add_0d binary_broadcast_add_1d binary_broadcast_add_2d binary_broadcast_add_3d binary_broadcast_add_4d; do echo "=== $f ==="; cat src/shader/webgpu/shadersources/standard/$f.glsl; done
```

- [ ] **Step 2: 7 本の `.wgsl` を作成**

翻訳ガイドに従い各ファイルを作成する。`relu.wgsl` と `binary_broadcast_add_2d.wgsl` は上部の完全例（原本と一致確認の上）。`binary_elementwise_add.wgsl` は relu と同型で 3 バッファ（a,b,c）+ Meta{len}、本体 `array_c[i] = array_a[i] + array_b[i]`。`binary_broadcast_add_{0,1,3,4}d.wgsl` は 2d 例を次元数に合わせて拡張（0d は `if (global_id.x == 0u) { array_c[0] = array_a[0] + array_b[0]; }`、1d/3d/4d は Meta の shape/stride フィールド数と index 分解段数を原本に合わせる）。

- [ ] **Step 3: 生成して shaders.ts を作る**

Run:
```bash
# まだ conv/gemm の .wgsl は無いが、存在する .wgsl だけ埋め込まれる
node src/shader/webgpu/compile.js
grep -c "binary_broadcast_add_2d" src/descriptor_runner/operators/webgpu/shaders.ts
```
Expected: 1（生成された shaders.ts に該当キーがある）。

- [ ] **Step 4: WGSL 構文の簡易検証（任意・WebGPU 対応 Node があれば）**

Run（無ければスキップ可。Task 9 のブラウザ検証で担保）:
```bash
node -e "const {webgpuShaders}=require('./src/descriptor_runner/operators/webgpu/shaders.ts'.replace('.ts',''))" 2>/dev/null || echo "skip (ts not directly requireable; validated in browser at Task 9)"
```

- [ ] **Step 5: コミット**

```bash
git add src/shader/webgpu/shadersources/standard/*.wgsl src/descriptor_runner/operators/webgpu/shaders.ts
git commit -m "feat(webgpu): add WGSL shaders for relu and binary (elementwise/broadcast)"
```
（注: shaders.ts は本来 generated だが tracked。WGSL 化に伴い内容が変わるため一度コミットする。Task 4 で conv/gemm 追加後に再生成・再コミットする。）

---

## Task 4: WGSL シェーダの作成（gemm / conv 系 5 本）

**Files:**
- Create: `src/shader/webgpu/shadersources/standard/{gemm,conv_im2col,conv_matmul,conv_bias,conv_transpose}.wgsl`

gemm/conv は index 計算が複雑。原本に忠実に翻訳ガイドを適用する。これらは数値検証（Task 9）が特に重要。

- [ ] **Step 1: 原本を確認**

Run:
```bash
for f in gemm conv_im2col conv_matmul conv_bias conv_transpose; do echo "=== $f ==="; cat src/shader/webgpu/shadersources/standard/$f.glsl; done
```

- [ ] **Step 2: 5 本の `.wgsl` を作成（翻訳ガイド適用）**

各 Meta 構造体のフィールド順・型（`int`→`i32`, `uint`→`u32`）、バインディング番号、本体の整数 index 演算を原本に忠実に訳す。注意点:
- GLSL の `int` ループ変数・negative 値（pad 等）は WGSL では `i32`。`gl_GlobalInvocationID.x` は `u32` なので、`i32` ループで使う場合は `i32(global_id.x)` とキャストする（原本が `int(gl_GlobalInvocationID.x)` としている箇所に対応）。
- 配列アクセスのインデックスは WGSL では `u32` か `i32` で型一致が必要。負になり得る計算は `i32` で行い、範囲チェック後に `u32` へキャストして添字に使う（原本の `if (iny >= 0 && ...)` ガードを維持）。
- 浮動小数リテラルは `0.0`（`f32`）。

- [ ] **Step 3: 生成（全 12 本が揃う）**

Run:
```bash
node src/shader/webgpu/compile.js
node -e "const s=require('fs').readFileSync('src/descriptor_runner/operators/webgpu/shaders.ts','utf8'); for (const k of ['relu','binary_elementwise_add','binary_broadcast_add_0d','binary_broadcast_add_1d','binary_broadcast_add_2d','binary_broadcast_add_3d','binary_broadcast_add_4d','gemm','conv_im2col','conv_matmul','conv_bias','conv_transpose']) if(!s.includes(JSON.stringify(k))) throw new Error('missing '+k); console.log('all 12 shader keys present');"
```
Expected: `all 12 shader keys present`。

- [ ] **Step 4: typecheck（Task 1〜4 で webgpu が緑に戻る）**

Run:
```bash
npm run typecheck; echo "typecheck: $?"
```
Expected: exit 0。`webgpuShaders` が `Record<string,string>` になり、`createPipeline(name, webgpuShaders[name]: string, n)` の型が一致して緑になる。

- [ ] **Step 5: コミット**

```bash
git add src/shader/webgpu/shadersources/standard/*.wgsl src/descriptor_runner/operators/webgpu/shaders.ts
git commit -m "feat(webgpu): add WGSL shaders for gemm and conv (im2col/matmul/bias/transpose)"
```

---

## Task 5: 旧 GLSL 削除・glslang 除去・build:all 復帰

**Files:**
- Delete: `src/shader/webgpu/shadersources/standard/*.glsl`
- Modify: `package.json`

- [ ] **Step 1: 旧 GLSL を削除**

Run:
```bash
git rm src/shader/webgpu/shadersources/standard/*.glsl
```

- [ ] **Step 2: `@webgpu/glslang` を除去**

Run:
```bash
npm uninstall @webgpu/glslang
```

- [ ] **Step 3: `build:all` に `shader:webgpu` を戻す**

`package.json` の `build:all` を:
```json
    "build:all": "npm run shader:webgpu && npm run makeShaderList && npm run build",
```
（`shader:wasm`(emscripten) は引き続き P4 まで除外のまま。）

- [ ] **Step 4: フルビルド検証**

Run:
```bash
rm -rf dist
npm run build:all 2>&1 | tail -5; echo "build:all: $?"
ls dist/*.js | wc -l
grep -c "relu" dist/op-webgpu.js | head -1
```
Expected: build:all exit 0、dist に 9 バンドル、op-webgpu.js に WGSL（relu 等の文字列）が埋め込まれている。

- [ ] **Step 5: 全ゲート確認**

Run:
```bash
npm run typecheck && npm run lint && npm run format:check && npm run test:unit && echo "gates OK"
```
Expected: `gates OK`。WGSL を埋め込んだ shaders.ts が lint 対象外（ignore 済み）であることも確認。

- [ ] **Step 6: コミット**

```bash
git add package.json package-lock.json
git rm src/shader/webgpu/shadersources/standard/*.glsl 2>/dev/null
git commit -m "build(webgpu): remove GLSL sources and @webgpu/glslang; restore shader:webgpu in build:all"
```

---

## Task 6: WebGPU 検証用フィクスチャの追加

**Files:**
- Modify: `test/fixtures/generate_fixtures.py`

WebGPU 対応 op（Relu/Add/Gemm/Conv）を実際に通すフィクスチャを追加する。relu/add は既存。gemm/conv を足す。

- [ ] **Step 1: `generate_fixtures.py` の `main()` に gemm/conv を追加**

`main()` 内、`sigmoid` の後に追記:
```python
    # gemm: Y = alpha*(A@B) + beta*C  (A: MxK, B: KxN, C: N)
    M, K, N = 2, 3, 4
    A = rng.standard_normal((M, K)).astype(np.float32)
    B = rng.standard_normal((K, N)).astype(np.float32)
    C = rng.standard_normal((N,)).astype(np.float32)
    gemm_inputs = [
        helper.make_tensor_value_info("input_0", TensorProto.FLOAT, [M, K]),
        helper.make_tensor_value_info("input_1", TensorProto.FLOAT, [K, N]),
        helper.make_tensor_value_info("input_2", TensorProto.FLOAT, [N]),
    ]
    gemm_out = helper.make_tensor_value_info("output_0", TensorProto.FLOAT, [M, N])
    gemm_node = helper.make_node("Gemm", ["input_0", "input_1", "input_2"], ["output_0"], alpha=1.0, beta=1.0)
    gemm_graph = helper.make_graph([gemm_node], "gemm_graph", gemm_inputs, [gemm_out])
    gemm_model = helper.make_model(gemm_graph, opset_imports=[helper.make_opsetid("", 13)])
    gemm_model.ir_version = 9
    onnx.checker.check_model(gemm_model)
    dump_case("gemm", gemm_model, {"input_0": A, "input_1": B, "input_2": C})
    cases.append({"name": "gemm", "large": False})

    # conv: 1 batch, 1 in-ch, 1 out-ch, 3x3 input, 2x2 kernel, no pad, stride 1
    Xc = rng.standard_normal((1, 1, 3, 3)).astype(np.float32)
    Wc = rng.standard_normal((1, 1, 2, 2)).astype(np.float32)
    conv_inputs = [
        helper.make_tensor_value_info("input_0", TensorProto.FLOAT, [1, 1, 3, 3]),
        helper.make_tensor_value_info("input_1", TensorProto.FLOAT, [1, 1, 2, 2]),
    ]
    conv_out = helper.make_tensor_value_info("output_0", TensorProto.FLOAT, [1, 1, 2, 2])
    conv_node = helper.make_node("Conv", ["input_0", "input_1"], ["output_0"], kernel_shape=[2, 2])
    conv_graph = helper.make_graph([conv_node], "conv_graph", conv_inputs, [conv_out])
    conv_model = helper.make_model(conv_graph, opset_imports=[helper.make_opsetid("", 13)])
    conv_model.ir_version = 9
    onnx.checker.check_model(conv_model)
    dump_case("conv", conv_model, {"input_0": Xc, "input_1": Wc})
    cases.append({"name": "conv", "large": False})
```

- [ ] **Step 2: 生成して確認**

Run:
```bash
npm run fixtures
cat test/model_test/runner/model/cases.json
head -c 4 test/model_test/runner/model/gemm/expected.bin; echo
head -c 4 test/model_test/runner/model/conv/expected.bin; echo
```
Expected: cases.json に relu/add/sigmoid/gemm/conv の 5 件、gemm/conv の expected.bin が `WDN2`。

- [ ] **Step 3: コミット**

```bash
git add test/fixtures/generate_fixtures.py
git commit -m "test(webgpu): add gemm/conv fixtures to exercise WebGPU ops"
```

---

## Task 7: CPU 経路の回帰確認（WGSL 化が CPU を壊していないこと）

**Files:** なし（検証のみ）

- [ ] **Step 1: CPU 経路 E2E と全ゲート**

Run:
```bash
npm run build
npm run fixtures
npm run test:unit && echo "unit OK"
npm run test:e2e 2>&1 | tail -3
```
Expected: unit 緑、Playwright CPU テスト PASS（relu/add/sigmoid/gemm/conv が CPU バックエンドで `ALL OK`）。WGSL 化は WebGPU のみ触るため CPU 経路は不変のはず。新フィクスチャ（gemm/conv）が CPU でも通ることをここで確認。

- [ ] **Step 2: 失敗時の対応**

新フィクスチャ（gemm/conv）が CPU で失敗する場合、フィクスチャの shape/属性が CPU 実装の対応範囲外の可能性。`docs/baseline.md`/CPU operator 実装に照らし、対応する shape/属性へ調整（テスト容易な最小ケースに）。CPU が通らないものは WebGPU 検証もできないため、まず CPU で緑にする。

---

## Task 8: WebGPU 経路の自動検証ハーネス（可能なら開発機で実行）

**Files:**
- Create: `test/e2e/webgpu.spec.ts`
- Modify: `playwright.config.ts`

WebGPU 対応ブラウザがあれば Playwright で WebGPU バックエンドを自動検証する。無い/未対応なら skip し、人手の目視へ委ねる（サイレントに諦めない）。

- [ ] **Step 1: `playwright.config.ts` に WebGPU 有効化フラグを追加**

`projects` の chromium に launch 引数を追加（既存 project を置換）:
```typescript
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        launchOptions: {
          args: ["--enable-unsafe-webgpu", "--enable-features=Vulkan"],
        },
      },
    },
  ],
```

- [ ] **Step 2: WebGPU スペックを作成（未対応なら skip）**

`test/e2e/webgpu.spec.ts`:
```typescript
import { test, expect } from "@playwright/test";

test("WebGPU backend runs WebGPU-supported ops and reports ALL OK", async ({ page }) => {
  await page.goto("/test/model_test/runner/standard.html");

  // Skip cleanly if this browser/GPU has no WebGPU (CI / unsupported machines).
  const hasWebGPU = await page.evaluate(() => "gpu" in navigator);
  test.skip(!hasWebGPU, "navigator.gpu unavailable; verify on a real GPU machine (docs/testing.md)");

  // Enable only the WebGPU backend checkbox (others off). Runner falls back to CPU
  // for ops WebGPU doesn't support, so ALL OK still means correctness.
  for (const cb of await page.locator('input[name="backend"]').all()) {
    const value = await cb.getAttribute("value");
    if (value === "webgpu") {
      if (!(await cb.isChecked())) await cb.check();
    } else if (await cb.isChecked()) {
      await cb.uncheck();
    }
  }

  await page.getByRole("button", { name: "Test" }).click();

  const summary = page.locator("#summary");
  await expect(summary).toBeVisible({ timeout: 100_000 });
  await expect(summary).toContainText("ALL OK");
  await expect(summary).toContainText("0 failed");
});
```

- [ ] **Step 3: 実行（開発機で WebGPU 有無を実測）**

Run:
```bash
npm run build && npm run fixtures
npm run test:e2e 2>&1 | tee /tmp/wd-webgpu-e2e.log
echo "exit: ${PIPESTATUS[0]}"
```
3 通りの結果を区別して報告すること:
- **PASS**: WebGPU 経路で全ケース ALL OK（WGSL 移行成功を自動実証）。
- **SKIPPED**: `navigator.gpu` 無し（このブラウザ/環境は WebGPU 非対応）。→ WGSL の正当性は人手の実 GPU 確認に委ねる（status へ記録）。
- **FAIL**: WebGPU は有効だが数値不一致/シェーダコンパイルエラー。→ 失敗 op と `page.on("console")` のエラーを採取し、該当 WGSL を原本と突き合わせて修正。デバッグ時のみ一時的に console リスナを足してよいが、コミット前に除去。**フィクスチャやランナーを甘くして通さないこと。**

- [ ] **Step 4: コミット**

```bash
git add playwright.config.ts test/e2e/webgpu.spec.ts
git commit -m "test(webgpu): add Playwright WebGPU spec (auto when navigator.gpu present)"
```

---

## Task 9: ドキュメント・status 更新と最終確認

**Files:**
- Modify: `docs/testing.md`, `docs/modernization-status.md`, `docs/baseline.md`

- [ ] **Step 1: `docs/testing.md` に WebGPU 検証を追記**

第 2 層の節に、`test/e2e/webgpu.spec.ts` は `navigator.gpu` がある開発機で WebGPU 経路を自動検証し、無ければ skip して第 3 層（実機目視）に委ねる旨を追記。

- [ ] **Step 2: `docs/baseline.md` に Phase 3 結果を追記**

WGSL 移行完了、glslang 除去、`build:all` への `shader:webgpu` 復帰、WebGPU E2E の結果（PASS/SKIPPED/対応ブラウザ）を記録。

- [ ] **Step 3: `docs/modernization-status.md` を更新**

P3 を完了にしチェック、現在地と次の一手を P4（WebGL/WASM/CPU 追従・onnx-proto→protobufjs・emscripten）へ。WebGPU 実 GPU の最終目視が未実施なら「人手が必要」に明記。

- [ ] **Step 4: 最終確認**

Run:
```bash
npm run typecheck && npm run lint && npm run format:check && npm run test:unit && npm run build:all && echo "ALL GATES OK"
npm run fixtures && npm run test:e2e 2>&1 | tail -5
```
Expected: 全ゲート緑、CPU E2E PASS、WebGPU E2E は PASS か SKIPPED（環境次第）。

- [ ] **Step 5: コミット**

```bash
git add docs/testing.md docs/baseline.md docs/modernization-status.md
git commit -m "docs(webgpu): record WGSL migration; advance status to P4"
```

---

## Self-Review（計画作成者による確認結果）

- **Spec coverage:** modernization-plan.md Phase 3 の項目 — 12 GLSL→WGSL（Task 3+4）、シェーダ生成刷新（Task 2）、現行 API 化（Task 1: computeStage→compute / dispatch→dispatchWorkgroups / endPass→end / shader Uint32Array→string）、glslang 除去・build:all 復帰（Task 5）、回帰検証（Task 7 CPU・Task 8 WebGPU）をカバー。
- **依存順:** Task 1（API string 化）→ Task 2（生成器・型）→ Task 3/4（WGSL 実体で型を緑へ）→ Task 5（旧資産除去）。Task 1〜4 は一連で typecheck を緑に戻すため連続実行が必須（Task 1 単独では赤い旨を明記）。
- **Type/名称整合:** `webgpuShaders: Record<string,string>`（compile.js 出力・スタブ・createPipeline 引数）で一貫。シェーダキー名は operators が参照する 12 個（`relu`/`binary_elementwise_add`/`binary_broadcast_add_{0..4}d`/`gemm`/`conv_im2col`/`conv_matmul`/`conv_bias`/`conv_transpose`）と一致。バインディング/Meta は「演算子側は変更しない」前提で WGSL を契約に合わせる。
- **検証現実:** WebGPU 数値検証は実 GPU 依存。Task 8 で PASS/SKIPPED/FAIL を区別し、SKIPPED 時は人手へ明示的に委譲（サイレントな省略なし）。CPU 回帰（Task 7）で WGSL 変更が CPU を壊さないことを担保。
- **placeholder:** relu / binary 系は完全 WGSL もしくは原本＋ガイド＋完全例で具体化。gemm/conv は原本（リポジトリ内）＋翻訳ガイド＋型/キャスト注意点＋数値検証ゲートで具体化。各タスクにコマンドと期待結果あり。

## 次フェーズ

P3 完了後、Phase 4（WebGL/WASM/CPU 追従 + onnx-proto→protobufjs + emscripten 導入）の個別計画を作成する。
