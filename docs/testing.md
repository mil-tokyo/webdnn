# テスト構成

WebDNN のテストは 3 層で構成する。**CI では GPU を使わない。**

## 第 1 層: ユニットテスト（vitest, GPU/DOM 不要, CI 常時）

- 対象: 純粋関数（`math`/`util`）、`CPUTensorImpl`、CPU 演算子（CPU コンテキスト経由）。
- 場所: `test/unit/**/*.test.ts`。バレル（`index.ts`）ではなく個別ソースを直接 import し、
  DOM/GPU 非依存に保つ（`test/unit/setup.ts` が `logging.ts` のための `window` を最小スタブ）。
- 実行: `npm run test:unit`（または `npm test`）。watch は `npm run test:watch`。
- CI: `.github/workflows/ci.yml` で `typecheck` / `lint` / `format:check` / `test:unit` / `build`
  を push・PR ごとに実行（GPU なし）。

## 第 2 層: Playwright 実機自動チェック（ローカル, CPU 経路）

- 対象: 実ブラウザ（chromium）でモデル推論を実行し、`expected.bin` と数値比較。
- 仕組み: `test/model_test/runner/standard.html` を Playwright で開き、backend チェックを
  すべて外して CPU のみ実行 → ランナーが付与する `#summary`（`ALL OK / 0 failed`）を判定。
- 前提: `npm run fixtures`（フィクスチャ生成）と `npm run build`（`dist/webdnn.js`）。
- 実行: `npm run test:e2e`。設定は `playwright.config.ts`（`npx http-server` を :8080 で自動起動）。
- 初回のみ `npx playwright install chromium` が必要。
- WebGL/WebGPU バックエンドは実 GPU が要るため、このヘッドレス E2E では検証しない（意図的）。
  実機でヘッド付き実行するか、第 3 層の目視で確認する。

## 第 3 層: 全ブラウザ目視確認（人手）

- 手順:
  1. `npm run build`
  2. `npm run fixtures`
  3. `npm run server`
  4. 各対象ブラウザ（Chrome / Edge / Safari / Firefox）で
     `http://localhost:8080/test/model_test/runner/standard.html` を開く。
  5. backend チェックボックス（wasm / webgl / webgpu）を選んで「Test」を実行。
  6. 末尾の `SUMMARY: ... ALL OK` を目視確認。
- 失敗時はページのログ（コンソール/結果リスト）を Claude に共有して原因調査する。
- 最適化モデル経路は `optimized.html`（`webdnn-core.js` + 動的 `op-*.js`）で確認する。

## フィクスチャ

- 生成器: `test/fixtures/generate_fixtures.py`（torch 非依存。`onnx.helper` で構築 →
  `onnxruntime` で期待値算出 → 既存 `serialize_tensors` で `WDN2` 形式の `expected.bin` 出力）。
- 依存は uv で pin（`test/fixtures/pyproject.toml` + `uv.lock`、Python 3.12）。
- 出力: `test/model_test/runner/model/<case>/{model.onnx,expected.bin}` と `cases.json`
  （現状: relu / add / sigmoid）。出力先は gitignore 対象で、`npm run fixtures` で再現する。
- ケース追加: `generate_fixtures.py` の `main()` に `dump_case(...)` を追記する。

## CI の範囲と限界

- CI（GitHub Actions, ubuntu）: 第 1 層 + ビルドのみ。GPU・実ブラウザ・emscripten は使わない。
- 第 2 層は実 GPU を持つ開発機での実行を想定（CI では走らせない）。
- 第 3 層と実 GPU 上の WebGPU/WebGL 最終確認は人手。
