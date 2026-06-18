# WebDNN 刷新 — Phase 2: 自動テスト基盤 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 回帰検証の網を 3 層（CI ユニット / 実機 Playwright / ブラウザ目視）で整え、CI では GPU を使わずに lint・typecheck・ユニットテスト・ビルドを常時緑にする。

**Architecture:** GPU/DOM 不要の純粋ロジックを vitest で Node 上でテストし GitHub Actions で常時実行する（第 1 層）。実 GPU を要する推論は、`npm run server` で配信したテストランナーを Playwright で実機ブラウザ駆動して CPU 参照と数値比較する（第 2 層）か、全対象ブラウザで URL を開いて目視確認する（第 3 層）。3 層は共通のテストフィクスチャ（`dump_direct_onnx` 由来の小さな ONNX + `expected.bin`）を参照する。

**Tech Stack:** vitest（Node 環境）, @playwright/test, GitHub Actions, uv（フィクスチャ生成用の pinned Python: onnx / onnxruntime / numpy。torch は使わない）, 既存の `WDN2` バイナリ形式（`serialize_tensors`）。

**上位計画:** [docs/modernization-plan.md](../modernization-plan.md) の Phase 2。前提（npm / Vite / typecheck / lint / format:check 緑）は P1 で整備済み。

**重要な前提（実行者向け）:**
- CI には **GPU テストを含めない**。CI = lint + typecheck + unit + build のみ。
- 第 2 層（Playwright 実機）と第 3 層（目視）は実 GPU・実ブラウザを要するため、CI では走らせない。Claude は**仕組みを構築**し、CPU バックエンド経路など GPU 不要部分のみヘッドレスで検証する。実 GPU バックエンドの最終確認は人手（status の「人手が必要」参照）。
- ユニットテストは DOM/GPU 非依存にするため、バレル（`index.ts`）ではなく**個別ソースモジュールを直接 import** する（`index.ts` は webgl/webgpu/wasm を巻き込み `document`/`navigator`/`Worker` に触れるため）。vitest の `environment` は `node`。

---

## ファイル構成

**作成:**
- `vitest.config.ts` — vitest 設定（node 環境、test ルート）
- `test/unit/math.test.ts` — 純粋関数（argmax/argmin/arange/arrayProd/Sum/Equal）
- `test/unit/random.test.ts` — `Random` の決定性
- `test/unit/cpuTensor.test.ts` — `CPUTensorImpl`（strides/getValue/setValue/constructor）
- `test/unit/cpuOperator.test.ts` — CPU 演算子（Relu）を CPU コンテキスト経由で
- `.github/workflows/ci.yml` — CI（GPU なし）
- `test/fixtures/generate_fixtures.py` — torch 非依存のフィクスチャ生成（onnx.helper + onnxruntime）
- `test/fixtures/pyproject.toml` — uv 管理の pinned Python 環境
- `playwright.config.ts` — Playwright 設定（webServer に `npm run server`）
- `test/e2e/model.spec.ts` — ランナーページを駆動し CPU 経路で全ケース OK を検証
- `docs/testing.md` — 3 層の説明と実行手順

**変更:**
- `package.json` — `test`/`test:unit`/`test:e2e`/`fixtures` scripts、devDependencies
- `test/model_test/runner/test.js` 等 — 目視ランナーの軽微刷新（dist 参照・結果集計の明確化）

---

## Task 1: vitest 導入と最初の純粋関数テスト（math）

**Files:**
- Create: `vitest.config.ts`, `test/unit/math.test.ts`
- Modify: `package.json`

- [ ] **Step 1: vitest を導入**

Run:
```bash
cd /Users/milhidaka/dev/webdnn
npm install -D vitest@^2.1.0
```

- [ ] **Step 2: `vitest.config.ts` を作成**

```typescript
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["test/unit/**/*.test.ts"],
    // E2E (Playwright) は別ランナー。ここには含めない。
    exclude: ["test/e2e/**", "node_modules/**"],
  },
});
```

- [ ] **Step 3: 失敗するテストを書く（math 純粋関数）**

`test/unit/math.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { argmax, argmin } from "../../src/descriptor_runner/math/argsort";
import {
  arange,
  arrayProd,
  arraySum,
  arrayEqual,
} from "../../src/descriptor_runner/util";

describe("argmax", () => {
  it("returns index of the single max by default", () => {
    expect(argmax([1, 3, 2])).toEqual([1]);
  });
  it("returns top-k indices", () => {
    const top2 = argmax([5, 1, 4, 2], 2);
    expect(top2).toEqual([0, 2]);
  });
});

describe("argmin", () => {
  it("returns index of the single min by default", () => {
    expect(argmin([1, 3, 2])).toEqual([0]);
  });
  it("accepts Int32Array", () => {
    expect(argmin(new Int32Array([4, 0, 9]))).toEqual([1]);
  });
});

describe("arange", () => {
  it("one-arg form counts from 0", () => {
    expect(arange(3)).toEqual([0, 1, 2]);
  });
  it("two-arg form", () => {
    expect(arange(2, 5)).toEqual([2, 3, 4]);
  });
  it("negative step counts down", () => {
    expect(arange(3, 0, -1)).toEqual([3, 2, 1]);
  });
});

describe("array helpers", () => {
  it("arrayProd multiplies all elements", () => {
    expect(arrayProd([2, 3, 4])).toBe(24);
  });
  it("arraySum adds all elements", () => {
    expect(arraySum([2, 3, 4])).toBe(9);
  });
  it("arrayEqual compares element-wise", () => {
    expect(arrayEqual([1, 2], [1, 2])).toBe(true);
    expect(arrayEqual([1, 2], [1, 3])).toBe(false);
  });
});
```

- [ ] **Step 4: 実行して失敗を確認（スクリプト未設定でも直接実行）**

Run: `npx vitest run test/unit/math.test.ts`
Expected: argmax/argmin の top-k 順序など、実装の戻り値と期待値が一致しない場合はここで判明する。**まず実行して実際の戻り値を確認**し、`argmax`/`argmin` の戻り順（quickselect で非 stable）の仕様に合わせて期待値を調整すること（実装が正、テストを実装に合わせる）。最終的に全 PASS にする。

- [ ] **Step 5: `package.json` に test スクリプトを設定**

`"test": "echo \"tests added in P2\""` を以下に置換し、隣に追加:
```json
    "test": "vitest run",
    "test:unit": "vitest run test/unit",
    "test:watch": "vitest",
```

- [ ] **Step 6: 緑を確認**

Run: `npm run test:unit`
Expected: 全テスト PASS、exit 0。

- [ ] **Step 7: コミット**

```bash
git add vitest.config.ts test/unit/math.test.ts package.json package-lock.json
git commit -m "test: add vitest with pure-function unit tests (math/util)"
```

---

## Task 2: Random の決定性テスト

**Files:**
- Create: `test/unit/random.test.ts`

- [ ] **Step 1: 失敗するテストを書く**

`test/unit/random.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { Random } from "../../src/descriptor_runner/math/random";

describe("Random", () => {
  it("is deterministic for a fixed seed", () => {
    const a = new Random(42);
    const b = new Random(42);
    const seqA = [a.random(), a.random(), a.random()];
    const seqB = [b.random(), b.random(), b.random()];
    expect(seqA).toEqual(seqB);
  });

  it("produces scalars in [0, 1)", () => {
    const r = new Random(1);
    for (let i = 0; i < 100; i++) {
      const v = r.random();
      expect(v).toBeGreaterThanOrEqual(0);
      expect(v).toBeLessThan(1);
    }
  });

  it("random(size) returns a Float32Array of that length", () => {
    const r = new Random(7);
    const vec = r.random(5);
    expect(vec).toBeInstanceOf(Float32Array);
    expect(vec.length).toBe(5);
  });

  it("different seeds diverge", () => {
    const a = new Random(1).random();
    const b = new Random(2).random();
    expect(a).not.toBe(b);
  });
});
```

- [ ] **Step 2: 実行して確認**

Run: `npx vitest run test/unit/random.test.ts`
Expected: PASS。もし `random(size)` のオーバーロード戻り値が想定と違えば、実装（`src/descriptor_runner/math/random.ts`）の実シグネチャに合わせてテストを調整。全 PASS にする。

- [ ] **Step 3: コミット**

```bash
git add test/unit/random.test.ts
git commit -m "test: add Random determinism unit tests"
```

---

## Task 3: CPUTensor のテスト

**Files:**
- Create: `test/unit/cpuTensor.test.ts`

- [ ] **Step 1: 失敗するテストを書く**

`test/unit/cpuTensor.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { CPUTensorImpl } from "../../src/descriptor_runner/backend/cpu/cpuTensorImpl";

describe("CPUTensorImpl", () => {
  it("allocates zero-filled data when none is given", () => {
    const t = new CPUTensorImpl([2, 3], "float32");
    expect(t.data).toBeInstanceOf(Float32Array);
    expect(t.data.length).toBe(6);
    expect(t.length).toBe(6);
    expect(t.ndim).toBe(2);
    expect(Array.from(t.dims)).toEqual([2, 3]);
  });

  it("computes row-major strides", () => {
    const t = new CPUTensorImpl([2, 3], "float32");
    // strides for [2,3] row-major are [3,1]
    expect(Array.from(t.strides)).toEqual([3, 1]);
  });

  it("wraps an external buffer", () => {
    const buf = new Float32Array([1, 2, 3, 4, 5, 6]);
    const t = new CPUTensorImpl([2, 3], "float32", buf);
    expect(t.data).toBe(buf);
    expect(t.useExternalBuffer).toBe(true);
  });

  it("getValue / setValue use index math", () => {
    const t = new CPUTensorImpl([2, 3], "float32", new Float32Array([1, 2, 3, 4, 5, 6]));
    expect(t.getValue([0, 0])).toBe(1);
    expect(t.getValue([1, 2])).toBe(6);
    t.setValue(99, [1, 1]);
    expect(t.getValue([1, 1])).toBe(99);
  });

  it("respects int32 dataType", () => {
    const t = new CPUTensorImpl([2], "int32");
    expect(t.data).toBeInstanceOf(Int32Array);
    expect(t.dataType).toBe("int32");
  });
});
```

- [ ] **Step 2: 実行して確認**

Run: `npx vitest run test/unit/cpuTensor.test.ts`
Expected: PASS。`strides` が exploration の記述（`tensorImpl.ts` の strides 計算）と一致するか確認。`[2,3]` の row-major strides は `[3,1]`。実装が異なれば実装に合わせてテストを修正（実装が正）。全 PASS にする。

- [ ] **Step 3: コミット**

```bash
git add test/unit/cpuTensor.test.ts
git commit -m "test: add CPUTensorImpl unit tests (strides/getValue/setValue)"
```

---

## Task 4: CPU 演算子（Relu）をコンテキスト経由でテスト

**Files:**
- Create: `test/unit/cpuOperator.test.ts`

CPU 演算子の中核は `CPUUnary.run(context, inputs)` 経由でしか呼べない（exploration 参照）。`WebDNNCPUContextImpl` は DOM/GPU 不要で初期化できる。演算子は `getOpEntries()` から `opType==="Relu"` の `factory()` で取得する。

- [ ] **Step 1: 失敗するテストを書く**

`test/unit/cpuOperator.test.ts`:
```typescript
import { describe, it, expect } from "vitest";
import { WebDNNCPUContextImpl } from "../../src/descriptor_runner/backend/cpu/cpuContextImpl";
import { CPUTensorImpl } from "../../src/descriptor_runner/backend/cpu/cpuTensorImpl";
import { getOpEntries } from "../../src/descriptor_runner/operators/cpu/operators/standard/unary";

describe("CPU Relu operator", () => {
  it("clamps negatives to zero, keeps positives", async () => {
    const ctx = new WebDNNCPUContextImpl();
    await ctx.initialize();

    const reluEntry = getOpEntries().find((e) => e.opType === "Relu");
    expect(reluEntry).toBeDefined();
    const relu = reluEntry!.factory();

    const input = new CPUTensorImpl([5], "float32", new Float32Array([-2, -0.5, 0, 1, 3]));
    const [output] = (await relu.run(ctx, [input])) as CPUTensorImpl[];

    expect(Array.from(output.data)).toEqual([0, 0, 0, 1, 3]);
    expect(Array.from(output.dims)).toEqual([5]);
  });
});
```

- [ ] **Step 2: 実行して確認**

Run: `npx vitest run test/unit/cpuOperator.test.ts`
Expected: PASS。もし `WebDNNCPUContextImpl` の import が DOM グローバル（`document` など）参照でエラーになる場合は、その import 連鎖を報告（BLOCKED）。CPU コンテキストは本来 DOM 非依存のはずだが、もし `happy-dom` が必要なら `vitest.config.ts` の該当テストだけ `environment` を切り替える方針を相談すること（安易に全体を jsdom 化しない）。全 PASS にする。

- [ ] **Step 3: コミット**

```bash
git add test/unit/cpuOperator.test.ts
git commit -m "test: add CPU Relu operator test via CPU context"
```

---

## Task 5: GitHub Actions CI（GPU なし）

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: ワークフローを作成**

`.github/workflows/ci.yml`:
```yaml
name: CI

on:
  push:
    branches: [master, modernization]
  pull_request:

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      # esbuild など postinstall を持つ依存のスクリプト実行を許可した上で install
      - run: npm ci
      - name: Generate operator entry list (no native toolchain needed)
        run: python3 scripts/make_operator_entries.py
      - run: npm run typecheck
      - run: npm run lint
      - run: npm run format:check
      - run: npm run test:unit
      - run: npm run build
```

補足:
- **GPU テストは含めない**（Playwright/目視は別運用）。
- `npm ci` は `package-lock.json` から決定的にインストールする。esbuild の postinstall は `npm ci` では既定で実行される（CI のクリーン環境では `npm approve-scripts` 等は不要だが、もし `--ignore-scripts` 相当でブロックされる場合は `npm rebuild esbuild` を追加する）。
- `make_operator_entries.py` を install 後に実行して `opEntriesAll.ts`（gitignore 対象）を生成し、`build`/`typecheck` の前提を満たす。`pretypecheck`/`prebuild:js` が `worker.ts`/`shaders.ts` スタブを補う。

- [ ] **Step 2: ローカルで CI 相当のコマンド列を検証**

Run:
```bash
python3 scripts/make_operator_entries.py
npm run typecheck && npm run lint && npm run format:check && npm run test:unit && npm run build
echo "all CI steps exit: $?"
```
Expected: 全ステップ緑、exit 0。

- [ ] **Step 3: ワークフロー YAML の構文を確認**

Run: `npx --yes js-yaml .github/workflows/ci.yml >/dev/null && echo "yaml ok"`
Expected: `yaml ok`（js-yaml が無ければ `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo ok` でも可）。

- [ ] **Step 4: コミット**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions (lint/typecheck/format/unit/build, no GPU)"
```

---

## Task 6: テストフィクスチャ生成（uv / torch 非依存）

**Files:**
- Create: `test/fixtures/pyproject.toml`, `test/fixtures/generate_fixtures.py`
- Modify: `package.json`

既存の `test/model_test/make_models.py` は torch を必須とする。第 2/3 層には軽量で再現可能なフィクスチャが必要なため、**torch 非依存**の生成器を新設する（`onnx.helper` でモデル構築 → `onnxruntime` で期待出力算出 → 既存 `serialize_tensors` で `expected.bin` 出力）。`uv` で Python 依存を pin する。

- [ ] **Step 1: `test/fixtures/pyproject.toml` を作成**

```toml
[project]
name = "webdnn-test-fixtures"
version = "0.0.0"
description = "Deterministic ONNX fixtures for WebDNN browser tests"
requires-python = ">=3.10"
dependencies = [
    "numpy==2.1.3",
    "onnx==1.17.0",
    "onnxruntime==1.20.1",
]
```

- [ ] **Step 2: 生成スクリプトを作成**

`test/fixtures/generate_fixtures.py`:
```python
"""Generate small, torch-free ONNX fixtures + expected.bin for browser tests.

Run with: uv run --project test/fixtures python test/fixtures/generate_fixtures.py
Outputs into test/model_test/runner/model/<case>/ and writes cases.json.
"""
import json
import os
import sys

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper

# Reuse the repo's WDN2 serializer (pure numpy, no torch).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "graph_transpiler"))
from webdnn.tensor_export import serialize_tensors  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "test", "model_test", "runner", "model")


def make_single_op_model(op_type, input_names, output_name, shape, attrs=None):
    inputs = [helper.make_tensor_value_info(n, TensorProto.FLOAT, shape) for n in input_names]
    output = helper.make_tensor_value_info(output_name, TensorProto.FLOAT, shape)
    node = helper.make_node(op_type, input_names, [output_name], **(attrs or {}))
    graph = helper.make_graph([node], f"{op_type}_graph", inputs, [output])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    model.ir_version = 9
    onnx.checker.check_model(model)
    return model


def dump_case(name, model, feeds):
    case_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(case_dir, exist_ok=True)
    onnx.save(model, os.path.join(case_dir, "model.onnx"))
    sess = ort.InferenceSession(
        model.SerializeToString(), providers=["CPUExecutionProvider"]
    )
    output_names = [o.name for o in sess.get_outputs()]
    outputs = sess.run(output_names, feeds)
    tensors = {}
    for n, arr in feeds.items():
        tensors[n] = np.ascontiguousarray(arr, dtype=np.float32)
    for n, arr in zip(output_names, outputs):
        tensors[n] = np.ascontiguousarray(arr, dtype=np.float32)
    serialize_tensors(os.path.join(case_dir, "expected.bin"), tensors)
    print("wrote", name)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rng = np.random.default_rng(0)
    cases = []

    # relu
    x = (rng.standard_normal((1, 8)).astype(np.float32))
    dump_case("relu", make_single_op_model("Relu", ["input_0"], "output_0", [1, 8]),
              {"input_0": x})
    cases.append({"name": "relu", "large": False})

    # add (two inputs)
    a = rng.standard_normal((1, 8)).astype(np.float32)
    b = rng.standard_normal((1, 8)).astype(np.float32)
    dump_case("add", make_single_op_model("Add", ["input_0", "input_1"], "output_0", [1, 8]),
              {"input_0": a, "input_1": b})
    cases.append({"name": "add", "large": False})

    # sigmoid
    x2 = rng.standard_normal((1, 8)).astype(np.float32)
    dump_case("sigmoid", make_single_op_model("Sigmoid", ["input_0"], "output_0", [1, 8]),
              {"input_0": x2})
    cases.append({"name": "sigmoid", "large": False})

    with open(os.path.join(OUTPUT_DIR, "cases.json"), "w", newline="\n") as f:
        json.dump(cases, f, indent=2)
    print("wrote cases.json with", len(cases), "cases")


if __name__ == "__main__":
    main()
```

補足: 生成 op（Relu/Add/Sigmoid）はいずれも CPU バックエンドが対応済みのはず。もし対応していない op があればテスト時に判明するので、その場合は対応済み op に差し替える。

- [ ] **Step 3: `package.json` に fixtures スクリプトを追加**

```json
    "fixtures": "uv run --project test/fixtures python test/fixtures/generate_fixtures.py",
```

- [ ] **Step 4: フィクスチャ生成を実行（uv 必須）**

Run:
```bash
uv --version || echo "NEED uv: install via 'curl -LsSf https://astral.sh/uv/install.sh | sh'"
npm run fixtures
ls test/model_test/runner/model/
cat test/model_test/runner/model/cases.json
```
Expected: `relu/`, `add/`, `sigmoid/` ディレクトリと各 `model.onnx`/`expected.bin`、`cases.json` が生成される。uv が無ければインストール（上記コマンド）。onnxruntime のホイール取得に時間がかかる場合がある。生成物（model 配下）は gitignore 対象か確認（`test/model_test/runner/.gitignore` を確認し、生成フィクスチャは原則コミットしない方針。小さいので必要ならコミット可だが、既定では生成手順をもって再現とする）。

- [ ] **Step 5: コミット（生成スクリプトと設定のみ。生成物は方針に従う）**

```bash
git add test/fixtures/pyproject.toml test/fixtures/generate_fixtures.py package.json
git status --short
git commit -m "test: add torch-free ONNX fixture generator (uv: onnx/onnxruntime)"
```
補足: `test/fixtures/uv.lock` が生成されたら一緒にコミットする（再現性のため）。生成された model/*/ をコミットするかは Step 4 の確認結果に従う。

---

## Task 7: ブラウザ目視テストランナーの刷新

**Files:**
- Modify: `test/model_test/runner/test.js`, `test/model_test/runner/standard.html`

既存ランナーは概ね動作する（exploration 参照: `#result`, name=`backend`, name=`large` の DOM、`cases.json` 取得、CPU と各バックエンドの数値比較）。第 3 層として「全ケース OK が一目で分かる」よう、結果サマリ（合計/成功/失敗）と全体ステータスの明示を加える。挙動（比較ロジック・許容誤差）は変えない。

- [ ] **Step 1: 現状ランナーが配信・起動するか確認**

Run:
```bash
npm run build   # dist/webdnn.js を最新化
npm run server &
sleep 2
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/test/model_test/runner/standard.html
pkill -f http-server 2>/dev/null || true
```
Expected: 200。

- [ ] **Step 2: 結果サマリ要素を追加（目視性向上）**

`test/model_test/runner/test.js` の `runTest` 内、全ケース完了後の集計表示を強化する。現状の「all ok」表示部分（`resultList.innerHTML += ...Done. All cases OK.`）の直前に、合計件数・成功件数・失敗件数のサマリ行を追加する。具体的には、ループ内で成功/失敗をカウントする変数 `let pass = 0, fail = 0;` を `allResults` 集計に併設し、完了後に:
```javascript
    const summary = document.createElement("p");
    summary.id = "summary";
    summary.className = allOk ? "result-ok" : "result-fail";
    summary.textContent = `SUMMARY: ${pass} passed / ${fail} failed / ${pass + fail} total — ${allOk ? "ALL OK" : "HAS FAILURES"}`;
    resultDom.appendChild(summary);
```
を追加する。`pass`/`fail` は各ケース判定箇所（`const ok = !msg;` の直後）で `if (ok) pass++; else fail++;` としてカウントする。`#summary` 要素は第 2 層（Playwright）が結果を機械判定するのに使う（Task 8）。

- [ ] **Step 3: 目視確認（人手・任意）**

ブラウザで `http://localhost:8080/test/model_test/runner/standard.html` を開き、Test ボタン押下で各ケースが走り、`SUMMARY: ... ALL OK` が出ることを確認する。GPU バックエンドのチェックボックスは実機で確認。**この目視は人手**。Claude は次タスク（Playwright）で CPU 経路の自動確認を行う。

- [ ] **Step 4: コミット**

```bash
git add test/model_test/runner/test.js test/model_test/runner/standard.html
git commit -m "test: add pass/fail summary to browser visual runner"
```

---

## Task 8: Playwright 実機ハーネス（CPU 経路を自動検証、GPU はローカル）

**Files:**
- Create: `playwright.config.ts`, `test/e2e/model.spec.ts`
- Modify: `package.json`

- [ ] **Step 1: Playwright を導入**

Run:
```bash
npm install -D @playwright/test@^1.48.0
npx playwright install chromium
```

- [ ] **Step 2: `playwright.config.ts` を作成**

```typescript
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "test/e2e",
  timeout: 120_000,
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL: "http://localhost:8080",
  },
  webServer: {
    command: "npx http-server -c-1 -p 8080 .",
    url: "http://localhost:8080/test/model_test/runner/standard.html",
    reuseExistingServer: true,
    timeout: 60_000,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
```

- [ ] **Step 3: E2E スペックを作成（CPU 経路で全ケース OK を判定）**

`test/e2e/model.spec.ts`:
```typescript
import { test, expect } from "@playwright/test";

// CPU バックエンドのみをヘッドレスで検証する（GPU 不要・CI 外のローカル実行）。
// WebGL/WebGPU は実 GPU が要るため、別途実機・目視で確認する（docs/testing.md）。
test("CPU backend runs all model cases and reports ALL OK", async ({ page }) => {
  await page.goto("/test/model_test/runner/standard.html");

  // backend チェックボックス（wasm/webgl/webgpu）は全て外す → CPU のみ実行。
  for (const cb of await page.getByRole("checkbox", { name: "backend" }).all()) {
    if (await cb.isChecked()) await cb.uncheck();
  }

  await page.getByRole("button", { name: "Test" }).click();

  const summary = page.locator("#summary");
  await expect(summary).toBeVisible({ timeout: 100_000 });
  await expect(summary).toContainText("ALL OK");
  await expect(summary).toContainText("0 failed");
});
```
補足: ランナーの checkbox の name 属性は `backend`（exploration 参照）。`getByRole("checkbox", { name: "backend" })` で name によるマッチが効かない場合は `page.locator('input[name="backend"]')` に置き換える。Test ボタンの文言は `standard.html` の `<button>Test</button>`。

- [ ] **Step 4: `package.json` に e2e スクリプトを追加**

```json
    "test:e2e": "playwright test",
```

- [ ] **Step 5: フィクスチャを用意して E2E 実行（CPU 経路）**

Run:
```bash
npm run fixtures           # Task 6 の生成器（uv）
npm run build              # dist/webdnn.js
npm run test:e2e 2>&1 | tee /tmp/wd-e2e.log
echo "e2e exit: ${PIPESTATUS[0]}"
```
Expected: chromium が起動し、CPU バックエンドで relu/add/sigmoid が `expected.bin` と一致、`#summary` が `ALL OK / 0 failed` を表示してテスト PASS。失敗時はログを精査し、ランナー側の DOM セレクタやフィクスチャ op 対応を修正。GPU バックエンドはこのスペックでは検証しない（意図的）。

- [ ] **Step 6: コミット**

```bash
git add playwright.config.ts test/e2e/model.spec.ts package.json package-lock.json
git commit -m "test: add Playwright harness verifying CPU backend on model fixtures"
```

---

## Task 9: テストドキュメントと status 更新

**Files:**
- Create: `docs/testing.md`
- Modify: `docs/modernization-status.md`

- [ ] **Step 1: `docs/testing.md` を作成**

3 層の役割・実行方法・CI 範囲・GPU は CI 非対象である旨・人手が必要な範囲を明記する:
```markdown
# テスト構成

WebDNN のテストは 3 層で構成する。**CI では GPU を使わない。**

## 第 1 層: ユニットテスト（vitest, GPU/DOM 不要, CI 常時）
- 対象: 純粋関数（math/util）、`CPUTensorImpl`、CPU 演算子（CPU コンテキスト経由）。
- 実行: `npm run test:unit`（または `npm test`）。
- CI: `.github/workflows/ci.yml` で lint/typecheck/format:check/unit/build を常時実行。

## 第 2 層: Playwright 実機自動チェック（ローカル, CPU 経路）
- 対象: ブラウザでモデル推論を実行し `expected.bin` と数値比較。
- 前提: `npm run fixtures`（uv: onnx/onnxruntime でフィクスチャ生成）。
- 実行: `npm run test:e2e`（chromium ヘッドレス, CPU バックエンド）。
- GPU バックエンド（WebGL/WebGPU）は実 GPU が要るため CI では走らせない。ローカル実機で
  目視（第 3 層）または Playwright のヘッド付き実行で確認する。

## 第 3 層: 全ブラウザ目視確認（人手）
- 手順: `npm run build` → `npm run fixtures` → `npm run server` → 各対象ブラウザ
  （Chrome/Edge/Safari/Firefox）で `http://localhost:8080/test/model_test/runner/standard.html`
  を開き、backend チェックボックスを選んで Test 実行 → `SUMMARY ... ALL OK` を目視。
- 失敗時はページのログを Claude に共有して原因調査。

## フィクスチャ
- `test/fixtures/generate_fixtures.py`（torch 非依存, uv 管理 pinned 環境）。
- 出力: `test/model_test/runner/model/<case>/{model.onnx,expected.bin}` と `cases.json`。
```

- [ ] **Step 2: status を更新**

`docs/modernization-status.md` の「現在地」「👉 次の一手」を P2 完了・次は P3 に更新し、P2 のチェックボックスを `[x]` にする。第 2/3 層の GPU 確認が人手であることを「人手が必要な作業」に追記。

- [ ] **Step 3: 最終検証（CI 相当 + e2e）**

Run:
```bash
python3 scripts/make_operator_entries.py
npm run typecheck && npm run lint && npm run format:check && npm run test:unit && npm run build && echo "CI-equiv OK"
npm run fixtures && npm run test:e2e && echo "E2E(CPU) OK"
```
Expected: 両方 OK。

- [ ] **Step 4: コミット**

```bash
git add docs/testing.md docs/modernization-status.md
git commit -m "docs: add testing guide; advance status to P3"
```

---

## Self-Review（計画作成者による確認結果）

- **Spec coverage:** modernization-plan.md Phase 2 の 3 層をカバー — 第 1 層（vitest + CI）= Task 1–5、第 2 層（Playwright 実機）= Task 8、第 3 層（ブラウザ目視）= Task 7、フィクスチャ固定（uv/torch 非依存）= Task 6、`docs/testing.md` = Task 9。CI に GPU を含めない方針を Task 5/8/9 で一貫。
- **Placeholder scan:** 各テスト/設定の実コードを記載。Task 6/8 の「op 差し替え」「セレクタ代替」は実行時の実測に基づく調整指示であり、具体的代替手段（`input[name="backend"]` 等）まで明示済み。
- **Type/名称整合:** `CPUTensorImpl`/`WebDNNCPUContextImpl`/`getOpEntries`/`argmax`/`argmin`/`arange`/`arrayProd`/`Random` は exploration の実シグネチャ（file:line 付）に一致。`#summary`（Task 7 で作成 → Task 8 で参照）、`cases.json` 形式（Task 6 生成 → ランナー consumes）、`expected.bin`（`serialize_tensors` 出力 → `TensorLoaderImpl` 読込）で一貫。
- **既知の前提:** ユニットテストは実装が正・テストを実装に合わせる旨を明記（argmax/argmin の非 stable 順序、strides 規約）。uv/onnxruntime/Playwright chromium のインストールが必要（ユーザー承認済みの「依存セットアップ OK」に該当）。

## 次フェーズ

P2 マージ後、Phase 3（WebGPU WGSL 移行）の個別計画を作成する。P3 は P2 の Playwright/目視ランナー（実 GPU）で WebGPU 経路を検証する。
