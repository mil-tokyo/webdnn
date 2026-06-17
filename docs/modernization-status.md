# モダナイゼーション進捗ステータス（living document）

> このファイルは刷新作業の **現在地と「次の一手」の単一の真実**。
> 1ステップでも進めたら必ずここを更新すること。CLAUDE.md からの入口。

最終更新: 2026-06-17

## 作業ブランチ

- 刷新作業は **`modernization` ブランチ** で行う（`master` には完成フェーズのみ取り込む）。
- 実行方式: Subagent-Driven（タスクごとに実装サブエージェント + spec/品質レビュー）。

## 現在地

- **現在フェーズ: Phase 2（自動テスト基盤）— 完了 ✅**
- 完了済み:
  - P0 ベースライン確立（[docs/baseline.md](baseline.md)、commit 3290804d）。
  - P1 全タスク（npm / Node 固定 / @webgpu/types 0.1.x / TS 5.9 / ESLint 9 flat / Prettier 3 / Vite）。
  - P2 全タスク（vitest 20件 / CI（GPUなし）/ uv フィクスチャ / 目視ランナー刷新 / Playwright CPU 経路 E2E / [docs/testing.md](testing.md)）。
- 到達状態（全て緑）: `typecheck`=0、`lint`=0、`format:check`=0、`build:all`=0（emscripten 不要）、`test:unit`=20 passed、`test:e2e`=CPU 経路 PASS（実 chromium で relu/add/sigmoid が onnxruntime と一致）、`dist` に 9 バンドル + dts。
- 完了した計画書:
  - [P0+P1](superpowers/plans/2026-06-17-p0-p1-baseline-and-toolchain.md)（全 Task 完了）
  - [P2](superpowers/plans/2026-06-17-p2-test-infrastructure.md)（全 Task 完了）

### 後続フェーズへ引き継ぐ重要事項
- `@webgpu/glslang`（GLSL→SPIR-V）はビルド自体は成功するが、現行ブラウザでは動かない。**P3** で WGSL 化し依存除去。
- WebGPU バックエンド旧 API 4 箇所は `@ts-expect-error` + `TODO(P3)` で切り分け済み。**P3** で除去（`webgpuContextImpl.ts`）。
- `shader:wasm`（emscripten）は `build:all` から除外。emscripten はシステムグローバル導入が必要（**P4** / 人手）。`worker.ts` は現在スタブ。
- `shader:webgpu` も `build:all` から除外（**P3** で WGSL 生成に置換後に再統合）。
- `makeShaderList`/`shader:wasm` は `python3` をハードコード。**P5** の uv 移行で `uv run` 化。
- クリーンインストール CI では esbuild の postinstall 承認が必要（**P2**）。
- `scripts/ensure-generated-stubs.mjs` が typecheck/build の前提スタブを補う（CI でも利用予定）。

## 👉 次の一手（NEXT STEP）

**Phase 3（WebGPU WGSL 移行）の個別計画を作成する。** ← 刷新の本丸
- 内容: `src/shader/webgpu/shadersources/standard/*.glsl`（12 本）を WGSL へ書き換え、
  `compile.js` を WGSL 文字列埋め込みに刷新、`webgpuContextImpl.ts` の旧 API（`@ts-expect-error` 済み 4 箇所:
  `computeStage`→`compute` / `dispatch`→`dispatchWorkgroups` / `endPass`→`end` / シェーダ型 Uint32Array→WGSL string）を現行化、
  `@webgpu/glslang` 除去、`shader:webgpu`/`shaders.ts` を WGSL 正規生成に戻し `build:all` へ再統合。
- 検証: P2 の Playwright（実機ヘッド付き）/ ブラウザ目視で WebGPU 経路を確認（**実 GPU は人手**）。
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
- [ ] **P3 WebGPU WGSL 移行** — 12 GLSL→WGSL・現行 API 化・glslang 除去 ← 次フェーズ
  - 計画書: 未作成（次に作成）
- [ ] **P4 WebGL/WASM/CPU 追従** — WebGL2 現行化・onnx-proto→protobufjs・emscripten 再現性
  - 計画書: 未作成
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
