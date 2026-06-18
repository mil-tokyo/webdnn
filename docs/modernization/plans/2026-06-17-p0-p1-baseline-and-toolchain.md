# WebDNN 刷新 — Phase 0 + Phase 1: ベースライン確立 & ツールチェーン刷新 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 現状ビルドの動作状況を実証的に記録した上で、開発基盤を npm / TypeScript 5 / ESLint 9 (flat) / Vite へ移行し、以降の全フェーズを型チェック・Lint で守れる土台を作る。

**Architecture:** まず Phase 0 で「移行前は何が動き何が壊れているか」を `docs/baseline.md` に固定する。次に Phase 1 で、後段の改修（特に P3 の WebGPU WGSL 移行）が安全網の下で進むよう、パッケージマネージャ・言語・Lint・ビルドを段階的に置き換える。WebGPU バックエンドの破壊的な型エラーは P3 で直すため、本フェーズでは `@ts-expect-error` + `TODO(P3)` で明示的に切り分けて typecheck を緑に保つ。

**Tech Stack:** Node LTS, npm, TypeScript 5.x, ESLint 9 (flat config), Prettier, Vite (build API by script), `@webgpu/types` 0.1.x。ランタイム本体は TypeScript（`src/descriptor_runner/`）。

**全体方針:** これは上位計画 [docs/modernization-plan.md](../modernization-plan.md) の Phase 0 と Phase 1 を対象とする。Phase 2〜5 は本計画マージ後に各フェーズ個別の計画として作成する。

**重要な前提（実行者向け）:**
- 本フェーズは**挙動を変えない**。成果物（dist）は Phase 0 で記録したベースラインと機能的に同等であること。
- TDD の「テストを先に書く」は機能追加向けの形式。本フェーズは設定移行が中心のため、各タスクの検証は「ビルド成功 / typecheck 緑 / lint 緑 / 出力ファイルの存在と同等性」を受け入れ基準（acceptance criteria）とする。
- 設定ファイルの内容は best-effort で記載している。実行時にエラーが出たら受け入れ基準を満たすまで調整すること（調整した内容はコミットメッセージに残す）。

---

## ファイル構成（このフェーズで作成/変更するファイル）

**作成:**
- `docs/baseline.md` — 移行前の動作状況マトリクス（Task 1）
- `.nvmrc` — Node バージョン固定（Task 3）
- `eslint.config.js` — ESLint 9 flat config（Task 6）
- `scripts/build.mjs` — Vite build API を用いた 9 バンドルの生成スクリプト（Task 7）
- `vite.config.ts` — Vite 共通設定（型チェック/IDE 用、build は build.mjs が駆動）（Task 7）

**変更:**
- `package.json` — PM=npm、依存更新、scripts 整理（Task 2,4,5,6,7,8）
- `tsconfig.json` — TS5 向け設定（Task 5）
- `src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts` — WebGPU 旧 API 呼び出しに `@ts-expect-error` + `TODO(P3)`（Task 4）

**削除:**
- `yarn.lock`（Task 2）
- `.eslintrc.json`（Task 6）
- `webpack.config.js` ほか 9 個の `webpack*.config.js`（Task 7）

---

## Task 1: Phase 0 — ベースライン確立

**Files:**
- Create: `docs/baseline.md`

- [ ] **Step 1: 依存をインストール（既存ツールのまま）**

Run:
```bash
cd /Users/milhidaka/dev/webdnn
yarn 2>&1 | tee /tmp/wd-yarn.log
```
Expected: インストール完了。失敗してもログを残して次へ進む（失敗内容は baseline に記録）。

- [ ] **Step 2: Python 側（graph_transpiler）をインストール**

Run:
```bash
python --version
python setup.py develop 2>&1 | tee /tmp/wd-pysetup.log
```
Expected: 成功または失敗。いずれもログを残す（Python 3.6 前提なので失敗の可能性あり）。

- [ ] **Step 3: 現状ビルドを試行し、各ステップの成否を記録**

Run（各コマンドの成否を個別に確認すること）:
```bash
npm run shader:webgpu 2>&1 | tee /tmp/wd-shader-webgpu.log
npm run shader:wasm   2>&1 | tee /tmp/wd-shader-wasm.log
npm run makeShaderList 2>&1 | tee /tmp/wd-shaderlist.log
npm run build         2>&1 | tee /tmp/wd-build.log
npm run build:core    2>&1 | tee /tmp/wd-build-core.log
npm run build:cpu && npm run build:wasm && npm run build:webgl1-4096 && npm run build:webgl1-16384 && npm run build:webgl2-4096 && npm run build:webgl2-16384 && npm run build:webgpu 2>&1 | tee /tmp/wd-build-ops.log
```
Expected: 一部成功・一部失敗が想定される（特に `shader:webgpu` は `@webgpu/glslang` 依存で失敗する可能性が高い）。各成否をログに残す。

- [ ] **Step 4: 生成された dist の一覧とサイズを記録**

Run:
```bash
ls -la dist/ 2>&1 | tee /tmp/wd-dist.log
shasum dist/*.js 2>/dev/null | tee /tmp/wd-dist-sha.log
```
Expected: 生成できたファイルの一覧。これが Phase 1 完了時の比較基準になる。

- [ ] **Step 5: CPU バックエンドのテストランナーが起動するか確認**

Run:
```bash
npm run server &
sleep 2
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/test/model_test/runner/standard.html
kill %1 2>/dev/null || true
```
Expected: `200`（HTML が配信される）。実ブラウザでの実行は Phase 2 で扱うため、ここでは配信確認のみ。

- [ ] **Step 6: `docs/baseline.md` を作成**

以下の構成で、Step 1〜5 の実測結果を記入する（数値・成否は実測値に置き換える）:

```markdown
# WebDNN 移行前ベースライン（YYYY-MM-DD 実測）

## 環境
- Node: <node -v>
- Python: <python --version>
- emscripten (emcc -v): <あれば / なければ "未インストール">

## 依存インストール
- `yarn`: 成功 / 失敗（要点）
- `python setup.py develop`: 成功 / 失敗（要点）

## ビルド成否
| ステップ | 結果 | 備考（失敗理由など） |
|----------|------|----------------------|
| shader:webgpu | OK/NG | |
| shader:wasm | OK/NG | |
| makeShaderList | OK/NG | |
| build (webdnn.js) | OK/NG | |
| build:core | OK/NG | |
| build:cpu/wasm/webgl*/webgpu | OK/NG | |

## 生成された dist
（ls -la dist/ の結果と各ファイルの shasum）

## バックエンド別の現状評価
- CPU: 動作見込み（テストランナー配信 200 を確認）
- WASM: <emscripten 有無に依存>
- WebGL: <ビルド成否>
- WebGPU: 現行ブラウザで非動作（旧 GLSL+SPIR-V 経路・旧 API）。詳細は P3 で対応。
```

- [ ] **Step 7: コミット**

```bash
git add docs/baseline.md
git commit -m "docs: record pre-migration baseline (P0)"
```

---

## Task 2: パッケージマネージャを npm に統一

**Files:**
- Delete: `yarn.lock`
- Create: `package-lock.json`（npm install により生成）

- [ ] **Step 1: yarn.lock を削除し node_modules をクリア**

Run:
```bash
cd /Users/milhidaka/dev/webdnn
rm -f yarn.lock
rm -rf node_modules
```

- [ ] **Step 2: npm でインストール（lockfile 生成）**

Run:
```bash
npm install 2>&1 | tee /tmp/wd-npm-install.log
```
Expected: `package-lock.json` が生成され、インストールが完了する。peer 依存の警告は許容。エラーで止まる場合は該当依存のバージョンを Task 4/5 の更新まで一旦据え置く。

- [ ] **Step 3: .gitignore に yarn 関連が残っていても害はないため変更不要（確認のみ）**

Run:
```bash
grep -n "yarn" .gitignore || echo "no yarn entries"
```
Expected: yarn-debug 等の汎用エントリのみ。削除不要。

- [ ] **Step 4: コミット**

```bash
git add -A
git commit -m "build: switch package manager from yarn to npm"
```

---

## Task 3: Node バージョン固定

**Files:**
- Create: `.nvmrc`
- Modify: `package.json`（`engines` 追加）

- [ ] **Step 1: `.nvmrc` を作成**

`.nvmrc`:
```
22
```
（実行環境の最新 LTS メジャー。`node -v` が 22 系でなければそのメジャーに合わせる。）

- [ ] **Step 2: `package.json` に engines を追加**

`package.json` の `"license": "MIT",` の直後に追加:
```json
  "engines": {
    "node": ">=20"
  },
```

- [ ] **Step 3: 確認**

Run:
```bash
node -e "console.log(require('./package.json').engines)"
```
Expected: `{ node: '>=20' }`

- [ ] **Step 4: コミット**

```bash
git add .nvmrc package.json
git commit -m "build: pin Node version (>=20) via .nvmrc and engines"
```

---

## Task 4: `@webgpu/types` を 0.1.x へ更新し、旧 API を P3 向けに切り分け

**Files:**
- Modify: `package.json`（`@webgpu/types`）
- Modify: `src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts`

このタスクの目的は、**WebGPU の破壊的変更を型エラーとして可視化**し、それを `@ts-expect-error` + `TODO(P3)` で明示的に切り分けて以降の typecheck を緑に保つこと。実際の WGSL/API 書き換えは Phase 3 で行う。

- [ ] **Step 1: `@webgpu/types` を最新へ更新**

Run:
```bash
npm install -D @webgpu/types@^0.1.40 2>&1 | tee /tmp/wd-webgpu-types.log
```
Expected: 0.1.x 系がインストールされる（具体版は最新に合わせる）。

- [ ] **Step 2: `tsconfig.json` の typeRoots を確認（後続 Task 5 で本格更新）**

現状の `typeRoots` は `["./node_modules/@webgpu/types", "./node_modules/@types"]`。このままで 0.1.x の型が読まれる。変更不要（Task 5 で `types` 指定に整理する）。

- [ ] **Step 3: WebGPU バックエンドの型エラーを洗い出す**

Run:
```bash
npx tsc --noEmit -p tsconfig.json 2>&1 | grep "backend/webgpu" | tee /tmp/wd-webgpu-typeerr.log
```
Expected: 少なくとも以下が報告される（新しい型定義では旧 API が存在しないため）:
- `webgpuContextImpl.ts` 内 `createComputePipeline({ ..., computeStage: ... })` の `computeStage`
- `passEncoder.dispatch(...)`
- `passEncoder.endPass()`

- [ ] **Step 4: 旧 API 呼び出し箇所に `@ts-expect-error` + `TODO(P3)` を付与**

`src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts` の該当箇所を以下のように変更する。

`createComputePipeline` の `computeStage`（現状）:
```typescript
      pipeline = device.createComputePipeline({
        layout: pipelineLayout,
        computeStage: {
          module: shaderModule,
          entryPoint: "main",
        },
      });
```
↓
```typescript
      pipeline = device.createComputePipeline({
        layout: pipelineLayout,
        // TODO(P3): migrate to current WebGPU API ({ compute: { module, entryPoint } })
        // @ts-expect-error legacy WebGPU API; rewritten in Phase 3 (WGSL migration)
        computeStage: {
          module: shaderModule,
          entryPoint: "main",
        },
      });
```

`dispatch`（現状）:
```typescript
    passEncoder.dispatch(
      request.workGroups.x,
      request.workGroups.y,
      request.workGroups.z
    );
```
↓
```typescript
    // TODO(P3): rename to dispatchWorkgroups (current WebGPU API)
    // @ts-expect-error legacy WebGPU API; rewritten in Phase 3
    passEncoder.dispatch(
      request.workGroups.x,
      request.workGroups.y,
      request.workGroups.z
    );
```

`endPass`（現状）:
```typescript
    passEncoder.endPass();
```
↓
```typescript
    // TODO(P3): rename to end() (current WebGPU API)
    // @ts-expect-error legacy WebGPU API; rewritten in Phase 3
    passEncoder.endPass();
```

- [ ] **Step 5: 残る WebGPU 型エラーにも同じパターンを適用**

Run:
```bash
npx tsc --noEmit -p tsconfig.json 2>&1 | grep "backend/webgpu\|operators/webgpu" | tee /tmp/wd-webgpu-typeerr2.log
```
Step 4 で消えなかった WebGPU 関連の型エラーが残っていれば、各該当行の直前に同じ 2 行コメント（`// TODO(P3): ...` と `// @ts-expect-error legacy WebGPU API; rewritten in Phase 3`）を付与する。WebGPU バックエンド（`backend/webgpu/`・`operators/webgpu/`）以外でエラーが出た場合は切り分けず、原因を調査して報告すること（本タスクの想定外）。

Expected: 最終的に `npx tsc --noEmit` の出力に `webgpu` 関連エラーが 0 件。

- [ ] **Step 6: コミット**

```bash
git add package.json package-lock.json src/descriptor_runner/backend/webgpu/webgpuContextImpl.ts
git commit -m "build: update @webgpu/types to 0.1.x; isolate legacy WebGPU API for P3"
```

---

## Task 5: TypeScript 5.x への更新と tsconfig 整理

**Files:**
- Modify: `package.json`（`typescript`）
- Modify: `tsconfig.json`

- [ ] **Step 1: TypeScript を 5.x へ更新**

Run:
```bash
npm install -D typescript@^5.5.0 2>&1 | tee /tmp/wd-ts5.log
npx tsc --version
```
Expected: `Version 5.x.x`

- [ ] **Step 2: `tsconfig.json` を更新**

`tsconfig.json` を以下の内容に置き換える:
```json
{
  "compilerOptions": {
    "target": "es2020",
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "skipLibCheck": true,
    "declaration": true,
    "emitDeclarationOnly": false,
    "noEmit": true,
    "pretty": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "newLine": "lf",
    "lib": ["es2020", "dom", "dom.iterable"],
    "types": ["@webgpu/types"]
  },
  "include": ["src/descriptor_runner"]
}
```
補足: 実トランスパイルは Vite(esbuild) が行うため tsconfig は `noEmit: true` の typecheck 用に切り替える。`types: ["@webgpu/types"]` で旧 `typeRoots` 指定を置き換える。

- [ ] **Step 3: typecheck を実行**

Run:
```bash
npx tsc --noEmit -p tsconfig.json 2>&1 | tee /tmp/wd-tsc-after.log
echo "exit: $?"
```
Expected: エラー 0 件（Task 4 の `@ts-expect-error` で WebGPU は切り分け済み）。`module: esnext` 化で新たな import 関連エラーが出た場合は該当 import を修正する。

- [ ] **Step 4: コミット**

```bash
git add package.json package-lock.json tsconfig.json
git commit -m "build: upgrade TypeScript to 5.x and modernize tsconfig (noEmit typecheck)"
```

---

## Task 6: ESLint 9 (flat config) + Prettier への移行

**Files:**
- Delete: `.eslintrc.json`
- Create: `eslint.config.js`
- Modify: `package.json`（eslint 関連依存と scripts）

- [ ] **Step 1: ESLint 9 系の依存へ更新**

Run:
```bash
npm install -D eslint@^9.9.0 typescript-eslint@^8.0.0 eslint-config-prettier@^9.1.0 prettier@^3.3.0 2>&1 | tee /tmp/wd-eslint9.log
npm uninstall @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-plugin-prettier 2>&1 | tee -a /tmp/wd-eslint9.log
```
補足: ESLint 9 では `typescript-eslint`（統合パッケージ）を使う。`eslint-plugin-prettier` は使わず、`eslint-config-prettier` で整形系ルールを無効化し、整形は `prettier` コマンドで別途行う方針に変更（flat config での実績ある構成）。

- [ ] **Step 2: `.eslintrc.json` を削除**

Run:
```bash
git rm .eslintrc.json
```

- [ ] **Step 3: `eslint.config.js` を作成**

`eslint.config.js`:
```javascript
// @ts-check
import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import prettierConfig from "eslint-config-prettier";

export default tseslint.config(
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      "src/descriptor_runner/operators/**/opEntries*.ts",
      "src/descriptor_runner/operators/webgpu/shaders.ts",
      "src/shader/**",
      "scripts/build.mjs",
    ],
  },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["src/descriptor_runner/**/*.ts"],
    languageOptions: {
      parserOptions: {
        project: "./tsconfig.json",
      },
    },
  },
  prettierConfig
);
```
補足: 自動生成ファイル（`opEntries*.ts`・`shaders.ts`）と shader ディレクトリは lint 対象外。`@eslint/js` は eslint 9 に同梱。

- [ ] **Step 4: `package.json` の eslint/prettier scripts を更新**

`scripts` 内の既存 `eslint` / `eslint:fix` を以下に置き換える:
```json
    "lint": "eslint src/descriptor_runner",
    "lint:fix": "eslint --fix src/descriptor_runner",
    "format": "prettier --write \"src/descriptor_runner/**/*.ts\"",
    "format:check": "prettier --check \"src/descriptor_runner/**/*.ts\"",
```

- [ ] **Step 5: lint を実行して緑にする**

Run:
```bash
npm run lint 2>&1 | tee /tmp/wd-lint.log
echo "exit: $?"
```
Expected: エラー 0 件。新ルールで既存コードに違反が出た場合は、(a) 自明な修正は `npm run lint:fix` で適用、(b) 大量に出る規約変更は該当ルールを `eslint.config.js` の最終ブロックで `"off"` または `"warn"` に調整（挙動を変えない範囲で）。調整したルールはコミットメッセージに列挙する。

- [ ] **Step 6: コミット**

```bash
git add -A
git commit -m "build: migrate to ESLint 9 flat config + standalone Prettier"
```

---

## Task 7: ビルドを webpack から Vite へ移行

**Files:**
- Create: `vite.config.ts`
- Create: `scripts/build.mjs`
- Modify: `package.json`（依存・scripts）
- Delete: `webpack.config.js`, `webpack-core.config.js`, `webpack-cpu.config.js`, `webpack-wasm.config.js`, `webpack-webgl1-4096.config.js`, `webpack-webgl1-16384.config.js`, `webpack-webgl2-4096.config.js`, `webpack-webgl2-16384.config.js`, `webpack-webgpu.config.js`

背景: 9 個の webpack config は以下の出力を生成する。WebGL の 4 出力は**同一エントリ・ビルド時定数なし**で、版とテクスチャサイズは実行時に決まる（`webglContextImpl.ts`）。よって 4 ファイルはバイト同一であり、1 回ビルドして 4 名へ複製すれば dist 互換を保てる。

| 出力ファイル | エントリ | グローバル名 |
|--------------|----------|--------------|
| webdnn.js | `index.ts` | WebDNN (umd) |
| webdnn-core.js | `separateBuild/coreOnly.ts` | WebDNN (umd) |
| op-cpu.js | `separateBuild/operatorCPU.ts` | なし (iife) |
| op-wasm.js | `separateBuild/operatorWasm.ts` | なし (iife) |
| op-webgpu.js | `separateBuild/operatorWebGPU.ts` | なし (iife) |
| op-webgl1-4096.js / -16384.js / op-webgl2-4096.js / -16384.js | `separateBuild/operatorWebGL.ts` | なし (iife)（4 ファイルは同一内容を複製） |

- [ ] **Step 1: Vite と vite-plugin-dts を導入し webpack 系を削除**

Run:
```bash
npm install -D vite@^5.4.0 vite-plugin-dts@^4.0.0 2>&1 | tee /tmp/wd-vite.log
npm uninstall webpack webpack-cli ts-loader 2>&1 | tee -a /tmp/wd-vite.log
git rm webpack.config.js webpack-core.config.js webpack-cpu.config.js webpack-wasm.config.js webpack-webgl1-4096.config.js webpack-webgl1-16384.config.js webpack-webgl2-4096.config.js webpack-webgl2-16384.config.js webpack-webgpu.config.js
```

- [ ] **Step 2: `vite.config.ts` を作成（IDE/型チェック用の最小設定）**

`vite.config.ts`:
```typescript
import { defineConfig } from "vite";

// 実ビルドは scripts/build.mjs が各エントリごとに Vite build API を呼ぶ。
// この設定は IDE と `vite` 単体実行時の共通既定値。
export default defineConfig({
  build: {
    target: "es2020",
    minify: false,
    emptyOutDir: false,
  },
});
```

- [ ] **Step 3: `scripts/build.mjs` を作成**

`scripts/build.mjs`:
```javascript
import { build } from "vite";
import { copyFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const outDir = resolve(root, "dist");

/** @type {{file:string, entry:string, name?:string, format:'umd'|'iife'}[]} */
const targets = [
  { file: "webdnn.js", entry: "src/descriptor_runner/index.ts", name: "WebDNN", format: "umd" },
  { file: "webdnn-core.js", entry: "src/descriptor_runner/separateBuild/coreOnly.ts", name: "WebDNN", format: "umd" },
  { file: "op-cpu.js", entry: "src/descriptor_runner/separateBuild/operatorCPU.ts", format: "iife" },
  { file: "op-wasm.js", entry: "src/descriptor_runner/separateBuild/operatorWasm.ts", format: "iife" },
  { file: "op-webgpu.js", entry: "src/descriptor_runner/separateBuild/operatorWebGPU.ts", format: "iife" },
  // WebGL: 1 回ビルドして 4 名へ複製
  { file: "op-webgl-base.js", entry: "src/descriptor_runner/separateBuild/operatorWebGL.ts", format: "iife" },
];

for (const t of targets) {
  await build({
    configFile: false,
    logLevel: "warn",
    build: {
      target: "es2020",
      minify: false,
      emptyOutDir: false,
      outDir,
      lib: {
        entry: resolve(root, t.entry),
        formats: [t.format],
        name: t.name ?? "WebDNNOp",
        fileName: () => t.file,
      },
    },
  });
  console.log("built", t.file);
}

// WebGL の 4 バリアントへ複製
const webglBase = resolve(outDir, "op-webgl-base.js");
for (const name of ["op-webgl1-4096.js", "op-webgl1-16384.js", "op-webgl2-4096.js", "op-webgl2-16384.js"]) {
  copyFileSync(webglBase, resolve(outDir, name));
  console.log("copied", name);
}
console.log("done");
```
補足: iife でグローバル名が不要なバンドルにも Vite は `name` を要求するためダミー（`WebDNNOp`）を渡す。出力は `op-*.js` の即時実行コードで、内部の `WebDNN` 参照は実行時にブラウザのグローバルへ解決される（webpack 版と同じ挙動）。

- [ ] **Step 4: `package.json` の build scripts を Vite ベースへ更新**

`scripts` の build 系を以下に置き換える（shader 生成系はそのまま残す。WebGPU の `shader:webgpu` は P3 で WGSL 化するまで失敗しうるが、本タスクでは触らない）:
```json
    "typecheck": "tsc --noEmit -p tsconfig.json",
    "build:js": "node scripts/build.mjs",
    "build:dts": "tsc -p tsconfig.json --emitDeclarationOnly --noEmit false --outDir dist/types",
    "build": "npm run build:js && npm run build:dts",
    "build:all": "npm run shader:wasm && npm run shader:webgpu && npm run makeShaderList && npm run build",
    "dev": "vite build --watch --config vite.config.ts",
    "server": "npx http-server -c-1",
    "test": "vitest run --passWithNoTests",
```
補足:
- `build:js` が 9 出力を生成。`build:dts` は型定義を `dist/types/` に出力（npm 配布の P5 で `exports` に接続）。
- 既存の `build:core` / `build:cpu` 等の個別 webpack scripts は削除する。
- `test` は Phase 2 で本格化するため、本フェーズでは vitest 未導入なら `"echo \"tests added in P2\""` に置き換えてよい（`exit 1` のままにはしない）。

- [ ] **Step 5: shader/makeShaderList の前提ファイルを用意してから JS ビルド**

`scripts/build.mjs` は `operators/*/opEntriesAll.ts` と `operators/webgpu/shaders.ts` を import 経由で必要とする（gitignore 対象の自動生成物）。WebGPU の SPIR-V 生成（`shader:webgpu`）は失敗しうるため、まず WASM 以外を生成し、`shaders.ts` が無ければ空スタブで通す。

Run:
```bash
npm run makeShaderList 2>&1 | tee /tmp/wd-makeshaderlist.log
# shaders.ts が未生成なら、ビルドを通すための空スタブを作成（P3 で正規生成に置換）
test -f src/descriptor_runner/operators/webgpu/shaders.ts || \
  printf 'export const webgpuShaders: Record<string, Uint32Array> = {};\n' > src/descriptor_runner/operators/webgpu/shaders.ts
```
Expected: `opEntriesAll.ts` 群が生成され、`shaders.ts` が存在する。

- [ ] **Step 6: JS ビルドを実行**

Run:
```bash
npm run build:js 2>&1 | tee /tmp/wd-vite-build.log
ls -la dist/*.js
```
Expected: 以下 9 ファイル + `op-webgl-base.js` が `dist/` に生成される: `webdnn.js`, `webdnn-core.js`, `op-cpu.js`, `op-wasm.js`, `op-webgpu.js`, `op-webgl1-4096.js`, `op-webgl1-16384.js`, `op-webgl2-4096.js`, `op-webgl2-16384.js`。エラーが出たら受け入れ基準（9 ファイル生成）を満たすまで `build.mjs`/エントリを調整。

- [ ] **Step 7: ベースラインとの出力対照**

Run:
```bash
diff <(ls dist/*.js | xargs -n1 basename | sort) <(printf '%s\n' op-cpu.js op-wasm.js op-webgl1-16384.js op-webgl1-4096.js op-webgl2-16384.js op-webgl2-4096.js op-webgl-base.js op-webgpu.js webdnn-core.js webdnn.js | sort) && echo "filenames OK"
```
Expected: `filenames OK`。Phase 0 の `docs/baseline.md` に記録した「生成できていた成果物」が、本タスク後も同じ名前で生成されていることを確認（`op-webgl-base.js` は新規の中間生成物）。

- [ ] **Step 8: コミット**

```bash
git add -A
git commit -m "build: migrate from webpack (9 configs) to Vite build script"
```

---

## Task 8: 統合検証と仕上げ

**Files:**
- Modify: `package.json`（最終確認）

- [ ] **Step 1: typecheck・lint・build を通しで実行**

Run:
```bash
npm run typecheck 2>&1 | tee /tmp/wd-final-typecheck.log; echo "typecheck exit: $?"
npm run lint 2>&1 | tee /tmp/wd-final-lint.log; echo "lint exit: $?"
npm run build:all 2>&1 | tee /tmp/wd-final-build.log; echo "build exit: $?"
```
Expected:
- typecheck: exit 0（WebGPU は `@ts-expect-error` で切り分け済み）
- lint: exit 0
- build:all: `shader:webgpu` は P3 まで失敗しうる。失敗する場合は `build:all` から `shader:webgpu` を一時的に外し（`"build:all": "npm run shader:wasm && npm run makeShaderList && npm run build"` とし、WGSL 化する P3 で戻す旨を `// P3 で shader:webgpu を復帰` とコミットメッセージに明記）、`npm run build` 部分が緑になることを確認する。

- [ ] **Step 2: dist が機能的に同等か簡易確認（CPU 経路の配信）**

Run:
```bash
npm run server &
sleep 2
curl -s -o /dev/null -w "standard.html: %{http_code}\n" http://localhost:8080/test/model_test/runner/standard.html
curl -s -o /dev/null -w "webdnn.js: %{http_code}\n" http://localhost:8080/dist/webdnn.js
kill %1 2>/dev/null || true
```
Expected: 両方 `200`。実ブラウザでの推論一致確認は Phase 2 で行う（本フェーズの範囲外）。

- [ ] **Step 3: baseline.md に移行後メモを追記**

`docs/baseline.md` の末尾に追記:
```markdown

## Phase 1 移行後（YYYY-MM-DD）
- パッケージマネージャ: npm（package-lock.json）
- TypeScript: 5.x / tsconfig は noEmit typecheck
- ESLint: 9 flat config / Prettier 単体
- ビルド: Vite（scripts/build.mjs）。dist の 9 出力を確認。
- 既知の積み残し: WebGPU バックエンド（P3 で WGSL 化）、shader:webgpu（P3 で復帰）。
```

- [ ] **Step 4: 最終コミット**

```bash
git add -A
git commit -m "chore: verify P0+P1 toolchain migration (typecheck/lint/build green)"
```

---

## Self-Review（計画作成者による確認結果）

- **Spec coverage:** modernization-plan.md の Phase 0（baseline）→ Task 1、Phase 1 の各項目（npm 統一 → Task 2、Node 固定 → Task 3、@webgpu/types 更新+切り分け → Task 4、TS5+tsconfig → Task 5、ESLint9 flat → Task 6、Vite 移行 → Task 7、scripts 整理 → Task 6/7、統合検証 → Task 8）をすべてカバー。onnx-proto 移行は P4、テスト基盤は P2 のため本計画では対象外（依存順どおり）。
- **Type/名称整合:** scripts 名（`typecheck`/`lint`/`build:js`/`build:dts`/`build`/`build:all`/`dev`/`server`/`test`）は Task 6〜8 で一貫。`op-webgl-base.js` は Task 7 で生成、Task 7 Step 7 の対照リストにも含めて整合。
- **積み残しの明示:** `shader:webgpu` 失敗時の扱い（P3 で復帰）と `shaders.ts` 空スタブ（P3 で正規生成へ）を Task 7/8 で明記。サイレントな省略なし。

---

## 次フェーズ

本計画マージ後、Phase 2（自動テスト基盤）の個別計画を作成する。Phase 2 は本フェーズで整った npm/Vite/typecheck/lint の上に vitest・Playwright・ブラウザ目視ランナー・CI を載せる。
