# モダナイゼーション進捗ステータス（living document）

> このファイルは刷新作業の **現在地と「次の一手」の単一の真実**。
> 1ステップでも進めたら必ずここを更新すること。CLAUDE.md からの入口。

最終更新: 2026-06-17

## 作業ブランチ

- 刷新作業は **`modernization` ブランチ** で行う（`master` には完成フェーズのみ取り込む）。
- 実行方式: Subagent-Driven（タスクごとに実装サブエージェント + spec/品質レビュー）。

## 現在地

- **現在フェーズ: Phase 3（WebGPU WGSL 移行）— 完了 ✅**
- 完了済み:
  - P0 ベースライン確立（[docs/baseline.md](baseline.md)、commit 3290804d）。
  - P1（npm / Node / @webgpu/types / TS 5.9 / ESLint 9 / Prettier 3 / Vite）。
  - P2（vitest 20件 / CI（GPUなし）/ uv フィクスチャ / 目視ランナー / Playwright CPU E2E / [docs/testing.md](testing.md)）。
  - P3（12 GLSL→WGSL / 現行 API 化 / glslang 除去 / gemm・conv フィクスチャ / **実 GPU で WebGPU E2E PASS**）。
- 到達状態（全て緑）: `typecheck`=0、`lint`=0、`format:check`=0、`build:all`=0（WGSL 生成込み・emscripten 不要）、`test:unit`=20 passed、`test:e2e`=CPU PASS + **WebGPU PASS**（実 chromium/Metal で relu/add/gemm/conv が onnxruntime と一致）、`dist` に 9 バンドル + dts。
- 完了した計画書:
  - [P0+P1](superpowers/plans/2026-06-17-p0-p1-baseline-and-toolchain.md)（全 Task 完了）
  - [P2](superpowers/plans/2026-06-17-p2-test-infrastructure.md)（全 Task 完了）
  - [P3](superpowers/plans/2026-06-17-p3-webgpu-wgsl.md)（全 Task 完了）

### 後続フェーズへ引き継ぐ重要事項
- `@webgpu/glslang`（GLSL→SPIR-V）はビルド自体は成功するが、現行ブラウザでは動かない。**P3** で WGSL 化し依存除去。
- WebGPU バックエンド旧 API 4 箇所は `@ts-expect-error` + `TODO(P3)` で切り分け済み。**P3** で除去（`webgpuContextImpl.ts`）。
- `shader:wasm`（emscripten）は `build:all` から除外。emscripten はシステムグローバル導入が必要（**P4** / 人手）。`worker.ts` は現在スタブ。
- `shader:webgpu` も `build:all` から除外（**P3** で WGSL 生成に置換後に再統合）。
- `makeShaderList`/`shader:wasm` は `python3` をハードコード。**P5** の uv 移行で `uv run` 化。
- クリーンインストール CI では esbuild の postinstall 承認が必要（**P2**）。
- `scripts/ensure-generated-stubs.mjs` が typecheck/build の前提スタブを補う（CI でも利用予定）。

## 👉 次の一手（NEXT STEP）

**Phase 4（WebGL / WASM / CPU 追従・依存更新）の個別計画を作成する。**
- 内容: WebGL2 コンテキスト取得・拡張の現行化と非推奨 API 確認、`onnx-proto`→protobufjs 生成
  バインディング移行、emscripten のシステムグローバル導入手順整備と `shader:wasm` 再現性
  （`worker.ts` スタブ→正規生成、`build:all` へ復帰）。
- 検証: P2/P3 の Playwright・目視ランナーで WebGL 経路を確認（**実 GPU/Safari は人手**）。
- 計画作成は writing-plans、実装は Subagent-Driven。

## 人手が必要な作業（Claude が実行できないもの）

- 実 GPU 上の WebGL/WebGPU 動作確認（第 3 層目視 / Playwright ヘッド付き）。失敗時はログを Claude へ。
- emscripten のシステムグローバル導入（**P4**。手順は Claude が提供、実行は手動）。
- `npm publish` / PyPI 公開（手動）。

## フェーズ一覧と進捗

上位計画: [docs/modernization-plan.md](modernization-plan.md)

- [x] **P0 ベースライン確立** — 現状の動作状況を `docs/baseline.md` に記録 ✅
- [x] **P1 ツールチェーン刷新** — npm / TS5 / ESLint9 flat / Vite / `@webgpu/types` 更新 ✅
  - 計画書: [2026-06-17-p0-p1-baseline-and-toolchain.md](superpowers/plans/2026-06-17-p0-p1-baseline-and-toolchain.md)（全 Task 完了）
- [x] **P2 自動テスト基盤** — vitest + 実機Playwright(CPU) + ブラウザ目視ランナー + CI（GPUなし）✅
  - 計画書: [2026-06-17-p2-test-infrastructure.md](superpowers/plans/2026-06-17-p2-test-infrastructure.md)（全 Task 完了）
- [x] **P3 WebGPU WGSL 移行** — 12 GLSL→WGSL・現行 API 化・glslang 除去・実GPUでE2E PASS ✅
  - 計画書: [2026-06-17-p3-webgpu-wgsl.md](superpowers/plans/2026-06-17-p3-webgpu-wgsl.md)（全 Task 完了）
- [ ] **P4 WebGL/WASM/CPU 追従** — WebGL2 現行化・onnx-proto→protobufjs・emscripten 再現性 ← 次フェーズ
  - 計画書: 未作成（次に作成）
- [ ] **P5 ドキュメント・配布整備** — README/CONTRIBUTING・uv 移行・npm 配布構成
  - 計画書: 未作成

## 既知の積み残し（フェーズをまたぐ TODO）

- `shader:webgpu`（GLSL→SPIR-V 生成）は P3 で WGSL 化するまで失敗しうる。P1 では `build:all` から一時的に外す可能性あり。
- `src/descriptor_runner/operators/webgpu/shaders.ts` は P1 で空スタブにする場合あり。P3 で正規生成へ。
- WebGPU バックエンドの旧 API 呼び出しは P1 で `@ts-expect-error` + `TODO(P3)` で切り分ける。P3 で除去。

## 人手が必要な作業（Claude が実行できないもの）

- 実機（Windows / Mac）での Playwright 実行、実 GPU 上の複数ブラウザでの目視確認（失敗時はログを Claude へ共有）。
- emscripten のシステムグローバル導入（手順は Claude が提供、実行は手動）。
- `npm publish` / PyPI 公開。

## 更新のしかた

ステップ完了時に最低限:
1. 「現在地」と「👉 次の一手」を書き換える。
2. 該当フェーズのチェックボックスを更新する。
3. 新たな積み残し・人手依頼が出たら該当セクションに追記する。
4. 「最終更新」日付を更新する。
