# WebDNN 刷新 — Phase 4: WebGL/WASM/CPU 追従・依存更新 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** メンテ終了の `onnx-proto` を protobufjs 生成バインディングへ置換し、WebGL2 経路を現行ブラウザで検証可能にし、emscripten/WASM ビルドを再現可能な手順として整備する。

**Architecture:** `onnx-proto`(npm) を、公式 `onnx.proto` から protobufjs で生成・ベンダリングした静的モジュール（`src/descriptor_runner/onnx/onnx.{js,d.ts}`）へ置換し、38 箇所の import を codemod で貼り替える。API（`onnx.ModelProto.decode` / `onnx.TensorProto.DataType` / `onnx.IAttributeProto` 等）は互換維持。WebGL は P2/P3 の Playwright/目視ランナーに WebGL バックエンドの検証を追加（実 GPU は人手）。emscripten はシステムグローバル導入手順を文書化し、`compile.py` を再現可能化、`worker.ts` の正規生成と `shader:wasm` の `build:all` 復帰は emcc 導入後（人手）。

**Tech Stack:** protobufjs + protobufjs-cli（pbjs/pbts）, 公式 onnx.proto, 既存 WebGL2 バックエンド, emscripten（手動導入）, P2/P3 のテスト基盤。

**上位計画:** [docs/modernization-plan.md](../../modernization-plan.md) Phase 4。前提 P1/P2/P3 完了済み。

**スコープ確定事項（探索済み）:**
- `onnx-proto` を import するファイルは **38 個**。使用シンボル: `onnx.IAttributeProto`(型)、`onnx.TensorProto.DataType`(enum)、`onnx.ModelProto`(型)、`onnx.IValueInfoProto`(型)、`onnx.ModelProto.decode`(実行時 1 箇所)。
- WebGL コンテキストは既に webgl2 優先 + webgl1 フォールバック + `EXT_color_buffer_float`/`half_float` を取得しており、大きな書き換えは不要。検証の追加が主。
- WASM は emcc 必須で `worker.ts`（現状スタブ）を生成する。emcc 導入は **人手**。

**実行者向け前提:**
- 各タスクで P1〜P3 のゲート（`typecheck`/`lint`/`format:check`/`test:unit`/`build:all` と CPU/WebGPU E2E）を緑に保つ。
- emscripten 関連（Task 6）は emcc が無い環境では「手順整備」までで、実ビルド検証は人手に委ねる（サイレントに通さない）。

---

## ファイル構成

**作成:**
- `src/descriptor_runner/onnx/onnx.js` + `src/descriptor_runner/onnx/onnx.d.ts` — protobufjs 生成（ベンダリング・コミット）
- `scripts/gen-onnx-proto.mjs` — 生成手順を再現するスクリプト（onnx.proto 取得 + pbjs/pbts）
- `test/e2e/webgl.spec.ts` — WebGL バックエンド E2E（GPU あれば自動、無ければ skip）
- `docs/emscripten-setup.md` — emscripten システムグローバル導入手順

**変更:**
- 38 個の `import { onnx } from "onnx-proto"` → ベンダリング先への相対 import（codemod）
- `package.json` — `onnx-proto` 除去、`protobufjs` を直接 dependency 化、`gen:onnx` script 追加、（emcc 導入後）`build:all` に `shader:wasm` 復帰
- `src/shader/wasm/compile.py` — emscripten/eigen バージョン固定・再現性向上
- `scripts/ensure-generated-stubs.mjs` — 必要なら onnx 生成物の扱いを追記（基本は不要）

---

## Task 1: protobufjs による onnx バインディング生成

**Files:**
- Create: `scripts/gen-onnx-proto.mjs`, `src/descriptor_runner/onnx/onnx.js`, `src/descriptor_runner/onnx/onnx.d.ts`
- Modify: `package.json`

- [ ] **Step 1: protobufjs と CLI を導入**

Run:
```bash
cd /Users/milhidaka/dev/webdnn
npm install protobufjs@^7.4.0
npm install -D protobufjs-cli@^1.1.3
```
（`protobufjs` は実行時に必要なので dependency。`protobufjs-cli` は生成時のみで devDependency。）

- [ ] **Step 2: 生成スクリプトを作成**

`scripts/gen-onnx-proto.mjs`:
```javascript
// Generate vendored protobufjs static bindings for ONNX from the official
// onnx.proto. Run: npm run gen:onnx
// Requires the onnx.proto file at scripts/onnx.proto (downloaded once, see README in this file).
import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const proto = resolve(root, "scripts", "onnx.proto");
const outDir = resolve(root, "src", "descriptor_runner", "onnx");
const jsOut = resolve(outDir, "onnx.js");
const dtsOut = resolve(outDir, "onnx.d.ts");

if (!existsSync(proto)) {
  console.error(
    "Missing scripts/onnx.proto. Download the official proto first, e.g.:\n" +
      "  curl -L -o scripts/onnx.proto https://raw.githubusercontent.com/onnx/onnx/v1.17.0/onnx/onnx.proto"
  );
  process.exit(1);
}

execFileSync(
  "npx",
  ["pbjs", "-t", "static-module", "-w", "es6", "--es6", "-o", jsOut, proto],
  { stdio: "inherit", cwd: root }
);
execFileSync("npx", ["pbts", "-o", dtsOut, jsOut], {
  stdio: "inherit",
  cwd: root,
});
console.log("generated", jsOut, dtsOut);
```

- [ ] **Step 3: onnx.proto を取得して生成**

Run:
```bash
curl -L -o scripts/onnx.proto https://raw.githubusercontent.com/onnx/onnx/v1.17.0/onnx/onnx.proto
node scripts/gen-onnx-proto.mjs
head -5 src/descriptor_runner/onnx/onnx.js
grep -c "ModelProto\|TensorProto\|AttributeProto\|ValueInfoProto" src/descriptor_runner/onnx/onnx.d.ts
```
Expected: `onnx.js`/`onnx.d.ts` が生成され、`onnx` 名前空間に `ModelProto`/`TensorProto`/`AttributeProto`/`IAttributeProto`/`IValueInfoProto` 等が含まれる。onnx.proto は `package onnx;` のため生成物は `export const onnx` 名前空間を持つ。

- [ ] **Step 4: 生成物が `onnx` を named export するか確認**

Run:
```bash
grep -n "export const onnx\|export { \$root\|onnx\b" src/descriptor_runner/onnx/onnx.js | head
```
Expected: ES6 出力で `onnx` 名前空間が export される。もし `pbjs --es6` の出力が `export const onnx` でなく `$root` ベースなら、`onnx/index.ts` を作って `import { onnx } from "./onnx.js"; export { onnx };` で正規化する（必要時のみ）。

- [ ] **Step 5: package.json に gen:onnx を追加し、生成物を lint/format/typecheck 対象外に**

`package.json` scripts に:
```json
    "gen:onnx": "node scripts/gen-onnx-proto.mjs",
```
`eslint.config.js` の ignores に `src/descriptor_runner/onnx/**` を追加。`.prettierignore` に `src/descriptor_runner/onnx/` を追加（生成物は整形しない）。

- [ ] **Step 6: コミット（依存と生成器・生成物・無視設定）**

```bash
git add package.json package-lock.json scripts/gen-onnx-proto.mjs scripts/onnx.proto src/descriptor_runner/onnx/ eslint.config.js .prettierignore
git commit -m "build(onnx): vendor protobufjs-generated onnx bindings (replaces onnx-proto)"
```
（注: 生成物 `onnx.js`/`onnx.d.ts` と `onnx.proto` はコミットする。再生成は `npm run gen:onnx`。）

---

## Task 2: import の貼り替え（codemod）と onnx-proto 除去

**Files:**
- Modify: 38 個の `*.ts`（`import { onnx } from "onnx-proto"`）
- Modify: `package.json`

- [ ] **Step 1: codemod スクリプトで import を相対パスへ貼り替え**

各ファイルの深さに応じた相対パスを計算して置換する。以下を一時スクリプトとして実行（実行後削除）:
```bash
node -e '
const fs=require("fs"), path=require("path"), cp=require("child_process");
const root=path.resolve("src/descriptor_runner");
const target=path.join(root,"onnx","onnx.js");
const files=cp.execSync("grep -rl \"from \\\"onnx-proto\\\"\" src/descriptor_runner",{encoding:"utf8"}).trim().split("\n");
for(const f of files){
  let rel=path.relative(path.dirname(f), path.join(root,"onnx","onnx"));
  if(!rel.startsWith("."))rel="./"+rel;
  rel=rel.split(path.sep).join("/");
  let s=fs.readFileSync(f,"utf8");
  s=s.replace(/from ["\x27]onnx-proto["\x27]/g, `from "${rel}"`);
  fs.writeFileSync(f,s);
  console.log("rewrote",f,"->",rel);
}
console.log("done",files.length,"files");
'
```
Expected: 38 ファイルの import が `from "../../onnx/onnx"`（深さに応じ可変）へ置換される。

- [ ] **Step 2: 残存 onnx-proto import が無いことを確認**

Run:
```bash
grep -rn "from \"onnx-proto\"\|from 'onnx-proto'" src/descriptor_runner/ && echo "STILL PRESENT (FAIL)" || echo "none (OK)"
```
Expected: `none (OK)`。

- [ ] **Step 3: onnx-proto を除去**

Run:
```bash
npm uninstall onnx-proto
grep -q "onnx-proto" package.json && echo "STILL in package.json" || echo "onnx-proto gone (OK)"
```

- [ ] **Step 4: 型チェック・lint・ビルド**

Run:
```bash
npm run typecheck 2>&1 | tail -20; echo "tc: ${PIPESTATUS[0]}"
npm run lint >/dev/null 2>&1; echo "lint: $?"
npm run build:all >/dev/null 2>&1; echo "build:all: $?"
```
Expected: 全て 0。protobufjs 生成物の型（`onnx.IAttributeProto`/`onnx.ModelProto`/`onnx.TensorProto.DataType` 等）が onnx-proto と互換であること。差異が出た場合（例: `ModelProto.decode` の戻り型、`DataType` enum の参照方法）は、該当箇所を最小修正で合わせる。生成物 `.js` の import 解決のため、`moduleResolution: bundler` 下で拡張子付き `onnx.js` を指す形が必要なら codemod のパスを `onnx/onnx.js` に調整する（typecheck エラーで判明したら対応）。

- [ ] **Step 5: 回帰テスト**

Run:
```bash
npm run test:unit >/dev/null 2>&1; echo "unit: $?"
npm run fixtures >/dev/null 2>&1 && npm run test:e2e 2>&1 | tail -4
```
Expected: unit 緑、CPU + WebGPU E2E PASS。protobufjs 置換がモデルロード（`ModelProto.decode`）を壊していないことを E2E（実モデルロード）で担保。

- [ ] **Step 6: コミット**

```bash
git add -A
git commit -m "refactor(onnx): replace onnx-proto imports with vendored bindings; drop onnx-proto dep"
```

---

## Task 3: WebGL2 経路の検証ハーネス追加

**Files:**
- Create: `test/e2e/webgl.spec.ts`

WebGL コンテキスト実装は概ね現行（webgl2 優先・float ext 取得）。書き換えより検証を追加し、現行ブラウザでの動作を担保する。

- [ ] **Step 1: WebGL E2E スペックを作成（webgpu.spec.ts と同型）**

`test/e2e/webgl.spec.ts`:
```typescript
import { test, expect } from "@playwright/test";

test("WebGL backend runs supported ops and reports ALL OK", async ({ page }) => {
  await page.goto("/test/model_test/runner/standard.html");

  // WebGL2 is broadly available, but headless GL can be flaky; skip cleanly if absent.
  const hasWebGL2 = await page.evaluate(() => {
    const c = document.createElement("canvas");
    return !!c.getContext("webgl2");
  });
  test.skip(!hasWebGL2, "WebGL2 unavailable in this headless browser; verify on a real machine");

  for (const cb of await page.locator('input[name="backend"]').all()) {
    const value = await cb.getAttribute("value");
    if (value === "webgl") {
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

- [ ] **Step 2: 実行（開発機で WebGL 有無を実測）**

Run:
```bash
npm run build && npm run fixtures
npx playwright test test/e2e/webgl.spec.ts 2>&1 | tee /tmp/wd-webgl-e2e.log
echo "exit: ${PIPESTATUS[0]}"
```
3 通りを区別して報告:
- **PASS**: WebGL 経路で全ケース ALL OK。
- **SKIPPED**: headless で WebGL2 無し → 実機目視へ委ねる（status へ記録）。
- **FAIL**: WebGL は有効だが数値不一致/コンパイルエラー → `page.on("console")` でエラー採取し、`backend/webgl/` の該当箇所を調査・最小修正。フィクスチャを甘くしない。
  （headless の WebGL は SwiftShader 等で float テクスチャ非対応の場合があり、その場合は SKIPPED 扱いとして明記。）

- [ ] **Step 3: コミット**

```bash
git add test/e2e/webgl.spec.ts
git commit -m "test(webgl): add Playwright WebGL spec (auto when WebGL2 present)"
```

---

## Task 4: WebGL バックエンドの非推奨パターン点検

**Files:**
- Modify: `src/descriptor_runner/backend/webgl/webglContextImpl.ts`（必要時のみ）

- [ ] **Step 1: 非推奨/要注意パターンを点検**

Run:
```bash
grep -n "getContext\|getExtension\|preserveDrawingBuffer\|UNSIGNED_BYTE\|texImage2D\|readPixels\|finish()\|flush()" src/descriptor_runner/backend/webgl/webglContextImpl.ts | head -40
```
確認観点:
- `getContext("webgl2", {...})` の属性（`powerPreference`, `failIfMajorPerformanceCaveat` 等）は現行で問題ないか。
- `EXT_color_buffer_float`/`half_float` の取得とフォールバックが現行ブラウザで妥当か。
- コンテキストロスト（`webglcontextlost`）ハンドリングの有無（無ければ握りつぶしを避け、最小限のエラーログ追加を検討。挙動は変えない）。

- [ ] **Step 2: 必要な最小修正のみ適用（なければスキップ）**

Task 3 の WebGL E2E が PASS していれば、現行ブラウザで動作している証拠。**動いているものは変えない**（YAGNI）。E2E で判明した実問題のみ最小修正する。修正不要なら本タスクは「点検済み・変更なし」を報告して次へ。

- [ ] **Step 3: 変更があればコミット**

```bash
git add src/descriptor_runner/backend/webgl/webglContextImpl.ts
git commit -m "fix(webgl): <具体的な修正内容>"
```
（変更が無ければコミット不要。）

---

## Task 5: emscripten/WASM の再現性整備（実ビルドは人手）

**Files:**
- Create: `docs/emscripten-setup.md`
- Modify: `src/shader/wasm/compile.py`

emcc はシステムグローバル導入が前提（容量大）。本タスクは**手順と再現性の整備**まで。`worker.ts` の正規生成と `shader:wasm` の `build:all` 復帰は emcc 導入後に人手で実施する。

- [ ] **Step 1: emscripten 導入手順を文書化**

`docs/emscripten-setup.md`:
```markdown
# emscripten のセットアップ（WASM バックエンドのビルド用）

WASM バックエンドの C++ カーネルは emscripten でビルドする。容量が大きいため
**システムグローバルに 1 度だけ導入**する（ワークツリー単位では入れない）。

## 推奨バージョン
- emscripten **3.1.x 以降**（本プロジェクトは `-O3` / `ALLOW_MEMORY_GROWTH=1` を使用）。

## 導入手順（emsdk）
```bash
git clone https://github.com/emscripten-core/emsdk.git ~/emsdk
cd ~/emsdk
./emsdk install latest
./emsdk activate latest
source ~/emsdk/emsdk_env.sh   # シェルごとに有効化（.zshrc 等に追記推奨）
emcc -v                        # 確認
```

## ビルド
```bash
npm run shader:wasm   # eigen を取得し emcc で worker をビルド、worker.ts を生成
```
成功後、`src/descriptor_runner/operators/wasm/worker/worker.ts` が実バイナリ埋め込み版に置き換わる
（普段は `scripts/ensure-generated-stubs.mjs` のスタブが使われている）。
```

- [ ] **Step 2: `compile.py` の再現性向上**

`src/shader/wasm/compile.py` を確認し、eigen のバージョンが固定（現状 3.3.9 がハードコード）であることを確認。`emcc` のバージョン非依存な書き方か点検し、必要なら以下を最小追加:
- eigen 取得失敗時の明確なエラーメッセージ（既に DL する作りなので、ハッシュ検証や再試行は任意）。
- 先頭コメントに「emcc が必要・`docs/emscripten-setup.md` 参照」を明記。
挙動は変えない（emcc が無い環境では従来どおり失敗してよい）。

- [ ] **Step 3: emcc の有無で分岐して検証**

Run:
```bash
if command -v emcc >/dev/null 2>&1; then
  echo "emcc present: $(emcc -v 2>&1 | head -1)"
  npm run shader:wasm 2>&1 | tail -5
  head -c 60 src/descriptor_runner/operators/wasm/operators/../worker/worker.ts
else
  echo "emcc ABSENT — WASM real build is a manual step (see docs/emscripten-setup.md). Skipping."
fi
```
- **emcc あり**: `shader:wasm` を実行し `worker.ts` が生成されること、`build:all` に `shader:wasm` を戻して WASM E2E（`test/e2e` に webgl 同様の wasm spec を足すかは任意）まで確認。
- **emcc なし**: 手順整備のみ完了とし、`build:all` への `shader:wasm` 復帰と worker.ts 正規生成は**人手 TODO** として status に明記（サイレントにしない）。

- [ ] **Step 4: コミット**

```bash
git add docs/emscripten-setup.md src/shader/wasm/compile.py
git commit -m "docs(wasm): add emscripten setup guide; note compile.py reproducibility"
```

---

## Task 6: ドキュメント・status 更新と最終確認

**Files:**
- Modify: `docs/testing.md`, `docs/baseline.md`, `docs/modernization-status.md`

- [ ] **Step 1: docs/testing.md に WebGL spec を追記**

第 2 層に `test/e2e/webgl.spec.ts`（WebGL2 があれば自動、無ければ skip）を追記。

- [ ] **Step 2: baseline.md に Phase 4 結果を追記**

onnx-proto→protobufjs 移行完了、WebGL E2E 結果（PASS/SKIPPED）、emscripten 手順整備と WASM の人手 TODO を記録。

- [ ] **Step 3: modernization-status.md を更新**

P4 を完了（emscripten 実ビルドが人手 TODO の場合はその旨明記）にチェック、次の一手を P5（ドキュメント・配布整備）へ。「人手が必要」に emscripten 実ビルド・WASM E2E・他ブラウザ WebGL を記載。

- [ ] **Step 4: 最終確認**

Run:
```bash
npm run typecheck && npm run lint && npm run format:check && npm run test:unit && npm run build:all && echo "GATES OK"
npm run fixtures && npm run test:e2e 2>&1 | tail -6
```
Expected: 全ゲート緑、CPU + WebGPU E2E PASS、WebGL E2E は PASS か SKIPPED。

- [ ] **Step 5: コミット**

```bash
git add docs/testing.md docs/baseline.md docs/modernization-status.md
git commit -m "docs: record P4 (onnx-proto->protobufjs, WebGL verify, emscripten guide); advance to P5"
```

---

## Self-Review（計画作成者による確認結果）

- **Spec coverage:** modernization-plan.md Phase 4 — onnx-proto→protobufjs（Task 1+2）、WebGL2 現行化・検証（Task 3+4）、emscripten 再現性・導入手順（Task 5）、CPU は基準として E2E で固定（Task 2/6 の回帰）をカバー。
- **依存順:** onnx 生成（T1）→ import 貼替・依存除去（T2）→ WebGL 検証（T3/T4）→ WASM/emscripten（T5）→ docs（T6）。T2 は実モデルロードを通る E2E で回帰検知。
- **Type/名称整合:** 生成 `onnx` 名前空間が `ModelProto.decode`/`TensorProto.DataType`/`IAttributeProto`/`IValueInfoProto`/`ModelProto` を提供し、38 箇所の既存使用と互換。codemod は深さ可変の相対パスを計算（単純 sed の誤りを回避）。
- **人手境界:** emscripten 実ビルド（T5）は emcc 必須のため分岐し、無ければ手順整備＋人手 TODO 明記（サイレント禁止）。WebGL/WASM の実 GPU・他ブラウザ確認は人手。
- **YAGNI:** WebGL は E2E が通れば変更しない方針（T4 は点検中心）。動いているコードを不要に書き換えない。

## 次フェーズ

P4 完了後、Phase 5（README/CONTRIBUTING 更新・uv 移行（graph_transpiler の `setup.py`→`pyproject.toml`）・npm 配布構成 `exports`/型定義・`prepublishOnly` のフレッシュクローン課題対応）の計画を作成する。
