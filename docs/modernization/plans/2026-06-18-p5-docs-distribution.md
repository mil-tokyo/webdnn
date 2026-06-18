# WebDNN 刷新 — Phase 5: ドキュメント・配布整備 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 刷新後の状態に合わせて README/CONTRIBUTING・アーキテクチャ文書を更新し、Python（graph_transpiler）を uv へ移行し、npm 配布構成を現行ビルド成果物に整合させる（最終フェーズ）。

**Architecture:** ドキュメントを現行のツール（npm / Vite / vitest / Playwright / uv フィクスチャ / WGSL）と対応ブラウザに合わせて書き直す。Python パッケージ `webdnn`（graph_transpiler）の `setup.py` を `pyproject.toml`（uv 管理）へ移行。`package.json` の `main`/`types`/`exports`/`files` を Vite の実出力（`dist/webdnn.js`・`dist/types/`）へ整合させ、`prepublishOnly` のフレッシュクローン課題（`build` が `makeShaderList` を含まず opEntries 未生成で失敗）を解消する。GPU・publish は不要/人手。

**Tech Stack:** Markdown ドキュメント, uv + pyproject.toml（PEP 621）, npm package.json（exports/types）。

**上位計画:** [docs/modernization-plan.md](../modernization-plan.md) Phase 5。前提 P1〜P4 完了済み。

**現状（探索済み）:**
- `README.md`/`README.ja.md` は旧情報（yarn・node 14・python 3.6・emscripten 2.0・「WebGPU は Chrome Canary のドラフト」「WSL」）。
- `package.json`: `main: "dist/index.js"`（**存在しないファイル**）、`types`/`exports` 未設定、`files: ["dist"]`、`prepublishOnly: "npm run build"`（`makeShaderList` を含まずフレッシュクローンで失敗）。
- Python パッケージ: `src/graph_transpiler/webdnn/`（`setup.py`、`install_requires=['numpy']`、version は package.json から動的取得）。
- 実 dist 出力: `dist/webdnn.js`(UMD, global `WebDNN`), `dist/webdnn-core.js`, `dist/op-*.js`(9 本), `dist/types/*.d.ts`。
- `requirements.test.txt`（torch 等）は旧 `make_models.py` 用。新フィクスチャは `test/fixtures`(uv)。

**実行者向け前提:**
- 純粋にドキュメント・設定。GPU 不要。各タスクで P1〜P4 ゲート（`typecheck`/`lint`/`format:check`/`test:unit`/`build:all`、CPU/WebGPU/WebGL E2E）を緑に保つ。
- publish（npm/PyPI）は実行しない（人手）。

---

## ファイル構成

**作成:**
- `pyproject.toml`（リポジトリ root、graph_transpiler 用、uv 管理）
- `docs/architecture.md`

**変更:**
- `README.md` / `README.ja.md` — 全面更新
- `CONTRIBUTING.md` — 開発/ビルド/テスト手順更新
- `package.json` — `main`/`types`/`exports`/`files`/`prepublishOnly` 整合

**削除:**
- `setup.py`（pyproject.toml へ移行後）

---

## Task 1: npm 配布構成の整合

**Files:**
- Modify: `package.json`

- [ ] **Step 1: main/types/exports/files を実出力へ整合**

`package.json` の該当フィールドを変更（`main` を実在ファイルへ、型と exports を追加）:
```json
  "main": "dist/webdnn.js",
  "types": "dist/types/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/types/index.d.ts",
      "default": "./dist/webdnn.js"
    },
    "./webdnn-core": "./dist/webdnn-core.js",
    "./dist/*": "./dist/*"
  },
  "files": [
    "dist"
  ],
```
（WebDNN は主に `<script>` タグで UMD グローバル `WebDNN` として使う。`exports` は npm/バンドラ利用者向けの最小限。`op-*.js` は実行時に動的ロードされるため `./dist/*` で公開する。）

- [ ] **Step 2: prepublishOnly のフレッシュクローン課題を解消**

`prepublishOnly` を `build:all` に変更し、公開前に opEntries 生成（`makeShaderList`）と WGSL 生成（`shader:webgpu`）が走るようにする:
```json
    "prepublishOnly": "npm run build:all",
```
（`build:all` は `shader:webgpu`(node) + `makeShaderList`(python3) + `build`。publish は python3 のある開発機で行う前提。`shader:wasm`(emscripten) は引き続き除外で、WASM を含めた公開は emscripten 導入後に `build:all` を更新してから行う旨を CONTRIBUTING に記す。）

- [ ] **Step 3: フレッシュ生成物を消してから build:all で再現性確認**

Run:
```bash
cd /Users/milhidaka/dev/webdnn
rm -rf dist src/descriptor_runner/operators/*/opEntriesAll.ts
npm run build:all 2>&1 | tail -5; echo "build:all: $?"
ls dist/webdnn.js dist/types/index.d.ts
node -e "const p=require('./package.json'); const fs=require('fs'); for (const f of [p.main, p.types]) if(!fs.existsSync(f)) throw new Error('missing '+f); console.log('main/types exist')"
```
Expected: build:all exit 0、`dist/webdnn.js` と `dist/types/index.d.ts` が存在し `main`/`types` と一致。

- [ ] **Step 4: パッケージ内容のドライラン**

Run:
```bash
npm pack --dry-run 2>&1 | tail -20
```
Expected: `dist/**`（webdnn.js, webdnn-core.js, op-*.js, types/）が含まれ、src やテストは含まれない。

- [ ] **Step 5: 全ゲート確認・コミット**

Run:
```bash
npm run typecheck && npm run lint && npm run build:all && echo "OK"
git add package.json
git commit -m "build(dist): fix main/types/exports to match Vite output; prepublishOnly runs build:all"
```

---

## Task 2: Python（graph_transpiler）の uv / pyproject.toml 移行

**Files:**
- Create: `pyproject.toml`
- Delete: `setup.py`

- [ ] **Step 1: `pyproject.toml` を作成**

リポジトリ root に作成（src レイアウト、setuptools バックエンド、uv で扱える PEP 621）:
```toml
[project]
name = "webdnn"
version = "2.0.0"
description = "WebDNN: ONNX inference runtime for web browsers (graph transpiler / optimizer)"
requires-python = ">=3.10"
dependencies = ["numpy"]
authors = [{ name = "Masatoshi Hidaka" }]
license = { text = "MIT" }
keywords = ["deep-neural-networks", "accelerate", "optimization", "javascript", "webgpu"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

[project.urls]
Homepage = "https://github.com/mil-tokyo/webdnn"

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src/graph_transpiler"]

[tool.setuptools.package-data]
"*" = ["*.js"]
```
（version は package.json と手動同期。`package_data ["*.js"]` は setup.py の踏襲。）

- [ ] **Step 2: setup.py を削除**

Run:
```bash
git rm setup.py
```

- [ ] **Step 3: uv で解決・インストールできることを確認**

Run:
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
uv sync 2>&1 | tail -10 || uv pip install -e . 2>&1 | tail -10
uv run python -c "import sys; sys.path.insert(0,'src/graph_transpiler'); import webdnn; print('webdnn import OK')"
```
Expected: 依存解決成功、`webdnn` パッケージが import できる。`uv sync` がルートに `.venv`/`uv.lock` を作る場合は `.gitignore` に `.venv/` があることを確認（無ければ追加）。`uv.lock` はコミットする。
（注: `webdnn` の import は `numpy` 等に依存。最小確認として `parse_onnx` などの import が通ればよい。)

- [ ] **Step 4: `.gitignore` 確認とコミット**

Run:
```bash
grep -q "^\.venv" .gitignore || printf "\n.venv/\n" >> .gitignore
git add pyproject.toml .gitignore
test -f uv.lock && git add uv.lock
git rm setup.py 2>/dev/null
git commit -m "build(python): migrate graph_transpiler from setup.py to pyproject.toml (uv)"
```

---

## Task 3: README の全面更新

**Files:**
- Modify: `README.md`, `README.ja.md`

- [ ] **Step 1: `README.md` を現行情報へ書き換え**

以下を反映（旧情報を一掃）:
- 概要: WebDNN v2（ONNX をブラウザで直接推論）。
- 対応バックエンド:
  - **WebGPU**: 現行の WGSL ベース。最新の Chrome/Edge（および対応する Safari/Firefox）で動作。
    （旧記述「Chrome Canary のドラフト」「WSL」「iOS13」は削除。）
  - **WebGL**: WebGL2 優先、WebGL1 フォールバック。
  - **WebAssembly**: emscripten ビルドが必要（[docs/emscripten-setup.md](docs/emscripten-setup.md) 参照）。
- 環境: Node.js 20+（`.nvmrc`）、Python 3.10+（uv）、（WASM 利用時のみ）emscripten 3.1+。
- セットアップ:
  ```
  npm install
  uv sync            # Python（モデル最適化）を使う場合
  ```
- ビルド:
  ```
  npm run build:all   # dist/webdnn.js, dist/webdnn-core.js, op-*.js, dist/types
  ```
- 基本的な使い方: 既存の `<script>` + `WebDNN.load(...)` の例は維持（API は不変）。
- テスト（[docs/testing.md](docs/testing.md) を参照する短いセクション）:
  ```
  npm test            # ユニット（vitest, GPU 不要）
  npm run fixtures    # テスト用 ONNX フィクスチャ生成（uv）
  npm run test:e2e    # Playwright（CPU/WebGPU/WebGL を自動検証）
  npm run server      # ブラウザ目視ランナー
  ```
  目視は `http://localhost:8080/test/model_test/runner/standard.html`。
- バージョン: alpha からの位置づけ（v2、ONNX 専用）を 1 文で。

旧 `make_models.py`（torch 依存）への言及は、新フィクスチャ（`npm run fixtures`）へ置き換える。`make_models.py` は大規模モデル生成用として残存する旨を必要なら 1 行補足。

- [ ] **Step 2: `README.ja.md` を同内容で日本語更新**

`README.md` と同じ構成・情報で日本語版を更新する。

- [ ] **Step 3: リンク・コマンドの妥当性確認**

Run:
```bash
grep -n "yarn\|Chrome Canary\|WSL\|python setup.py\|node.js 14\|emscripten 2" README.md README.ja.md && echo "STALE REMAINS (FIX)" || echo "no stale refs (OK)"
```
Expected: `no stale refs (OK)`。

- [ ] **Step 4: コミット**

```bash
git add README.md README.ja.md
git commit -m "docs: rewrite README for npm/Vite/uv/WGSL toolchain and current browsers"
```

---

## Task 4: CONTRIBUTING と architecture ドキュメント

**Files:**
- Modify: `CONTRIBUTING.md`
- Create: `docs/architecture.md`

- [ ] **Step 1: `CONTRIBUTING.md` を現行手順へ更新**

開発フローを記載: `npm install`、`npm run typecheck`/`lint`/`format`/`test`、`npm run build:all`、
`npm run test:e2e`（要 `npm run fixtures` と `npx playwright install chromium`）、
WGSL シェーダ編集時は `npm run shader:webgpu` で `shaders.ts` 再生成、
WASM 変更時は emscripten 必要（[docs/emscripten-setup.md](docs/emscripten-setup.md)）、
onnx バインディング再生成は `npm run gen:onnx`。コミット前ゲート（typecheck/lint/format:check/test:unit）を明記。

- [ ] **Step 2: `docs/architecture.md` を作成**

簡潔な構成図と各層の責務:
- `src/descriptor_runner/`（ランタイム: core / backend{cpu,wasm,webgl,webgpu} / operators / interface）
- シェーダ生成（`src/shader/webgpu` WGSL → `operators/webgpu/shaders.ts`、`src/shader/wasm` C++→wasm）
- onnx パース（`src/descriptor_runner/onnx`、protobufjs 生成）
- ビルド（Vite `scripts/build.mjs` → dist 9 バンドル + dts）
- Python `graph_transpiler`（オフライン最適化、`webdnn-core.js` 用）
- テスト 3 層（[docs/testing.md](docs/testing.md) 参照）
- 生成物スタブ（`scripts/ensure-generated-stubs.mjs`）

- [ ] **Step 3: コミット**

```bash
git add CONTRIBUTING.md docs/architecture.md
git commit -m "docs: update CONTRIBUTING; add architecture overview"
```

---

## Task 5: 最終確認・status 更新・全フェーズ完了記録

**Files:**
- Modify: `docs/modernization-status.md`, `docs/baseline.md`

- [ ] **Step 1: フルクリーンビルド + 全テスト**

Run:
```bash
export PATH="$HOME/.local/bin:$PATH"
rm -rf dist src/descriptor_runner/operators/*/opEntriesAll.ts
npm run typecheck && npm run lint && npm run format:check && npm run test:unit && npm run build:all && echo "GATES OK"
npm run fixtures && npm run test:e2e 2>&1 | tail -6
npm pack --dry-run 2>&1 | tail -5
```
Expected: 全ゲート緑、CPU/WebGPU/WebGL E2E PASS、pack に dist のみ。

- [ ] **Step 2: status を「全フェーズ完了（人手 TODO を除く）」に更新**

`docs/modernization-status.md`: P5 をチェック、現在地を「P0–P5 完了」に。残る人手 TODO
（emscripten/WASM、他ブラウザ実機、publish）と、master 未マージである旨を明記。次の一手は
「人手 TODO の消化 / master 取り込み判断」。

- [ ] **Step 3: baseline.md に Phase 5 結果を追記**

README/CONTRIBUTING/architecture 更新、uv 移行（setup.py 廃止）、npm 配布構成整合（main/types/exports、
prepublishOnly=build:all）を記録。

- [ ] **Step 4: コミット**

```bash
git add docs/modernization-status.md docs/baseline.md
git commit -m "docs: record P5 completion; modernization phases P0-P5 done (human TODOs remain)"
```

---

## Self-Review（計画作成者による確認結果）

- **Spec coverage:** modernization-plan.md Phase 5 — README/README.ja（Task 3）、CONTRIBUTING（Task 4）、
  architecture（Task 4）、uv 移行/`pyproject.toml`（Task 2）、npm 配布構成 `exports`/型定義/`files`（Task 1）、
  `prepublishOnly` フレッシュクローン課題（Task 1 Step 2、最終レビュー由来）をカバー。
- **依存順:** 配布構成（T1）→ Python uv（T2）→ README（T3）→ CONTRIBUTING/architecture（T4）→ 最終確認（T5）。
- **整合:** `main: dist/webdnn.js` / `types: dist/types/index.d.ts` は Vite 実出力（P1/P3 で確認済み）に一致。
  `prepublishOnly: build:all` は opEntries(makeShaderList)+WGSL(shader:webgpu) 生成を含み、フレッシュクローン
  ビルドを担保（Task1 Step3 で空状態から検証）。
- **人手境界:** WASM を含む配布は emscripten 導入後に `build:all` 更新が必要な旨を CONTRIBUTING/README に明記。
  publish は実行しない。
- **placeholder:** 各ドキュメントの記載項目を具体列挙、設定は完全な内容、検証コマンドと期待結果あり。

## 完了後

P0–P5 完了で自動実装可能な刷新は完了。残るは人手 TODO（emscripten 導入と WASM 検証、Safari/Firefox 実機確認、
npm/PyPI publish）と、`modernization` ブランチの master 取り込み判断。
