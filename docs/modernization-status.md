# モダナイゼーション進捗ステータス（living document）

> このファイルは刷新作業の **現在地と「次の一手」の単一の真実**。
> 1ステップでも進めたら必ずここを更新すること。CLAUDE.md からの入口。

最終更新: 2026-06-18

## 作業ブランチ

- 刷新作業は **`modernization` ブランチ** で行う（`master` には完成フェーズのみ取り込む）。
- 実行方式: Subagent-Driven（タスクごとに実装サブエージェント + spec/品質レビュー）。

## 現在地

- **現在フェーズ: Phase 5（ドキュメント・配布整備）— 完了 ✅（自動実装可能な刷新は P0–P5 で完了）**
- 完了済み: P0 / P1 / P2 / P3 / P4 / P5。
  - P3（12 GLSL→WGSL / 現行 API 化 / glslang 除去 / 実 GPU で WebGPU E2E PASS）。
  - P4（onnx-proto→protobufjs ベンダリング / WebGL E2E PASS / emscripten 手順整備）。
  - P5（README/README.ja/CONTRIBUTING 刷新 + `docs/architecture.md` 追加 / `setup.py`→`pyproject.toml`（uv）移行 / npm 配布構成 `main`・`types`・`exports` を Vite 実出力へ整合 / `prepublishOnly=build:all`）。
- 到達状態（全て緑）: `typecheck`=0、`lint`=0、`format:check`=0、`build:all`=0（emscripten 不要、クリーン状態から再現確認済み）、`test:unit`=20 passed、`test:e2e`=**CPU + WebGPU + WebGL の 3 経路 PASS**（実 chromium/Metal で onnxruntime と一致）、`dist` に 9 バンドル + dts、`npm pack` は dist のみ（155 files, src/test 非包含）、`uv sync` + `import webdnn` OK。
- 完了した計画書:
  - [P0+P1](superpowers/plans/2026-06-17-p0-p1-baseline-and-toolchain.md) / [P2](superpowers/plans/2026-06-17-p2-test-infrastructure.md) / [P3](superpowers/plans/2026-06-17-p3-webgpu-wgsl.md) / [P4](superpowers/plans/2026-06-17-p4-webgl-wasm-deps.md) / [P5](superpowers/plans/2026-06-18-p5-docs-distribution.md)（全 Task 完了）

### 後続フェーズへ引き継ぐ重要事項
- `@webgpu/glslang`（GLSL→SPIR-V）はビルド自体は成功するが、現行ブラウザでは動かない。**P3** で WGSL 化し依存除去。
- WebGPU バックエンド旧 API 4 箇所は `@ts-expect-error` + `TODO(P3)` で切り分け済み。**P3** で除去（`webgpuContextImpl.ts`）。
- `shader:wasm`（emscripten）は `build:all` から除外。emscripten はシステムグローバル導入が必要（**P4** / 人手）。`worker.ts` は現在スタブ。
- `shader:webgpu` も `build:all` から除外（**P3** で WGSL 生成に置換後に再統合）。
- `makeShaderList`/`shader:wasm` は `python3` をハードコード。**P5** の uv 移行で `uv run` 化。
- クリーンインストール CI では esbuild の postinstall 承認が必要（**P2**）。
- `scripts/ensure-generated-stubs.mjs` が typecheck/build の前提スタブを補う（CI でも利用予定）。

## 👉 次の一手（NEXT STEP）

**自動実装可能な刷新（P0–P5）は完了。残るは人手 TODO の消化と `master` 取り込み判断。**
- 人手 TODO（下記セクション参照）: emscripten/WASM 実ビルドと検証、Safari/Firefox 実機確認、npm/PyPI publish。
- `modernization` ブランチは **まだ `master` にマージしていない**。完了フェーズの取り込み判断は人手。

## 人手が必要な作業（Claude が実行できないもの）

- **emscripten のシステムグローバル導入** → `npm run shader:wasm` で `worker.ts` 正規生成 →
  `build:all` に `shader:wasm` 復帰 → WASM 経路の検証（手順: [emscripten-setup.md](emscripten-setup.md)）。
- 実 GPU 上の WebGPU/WebGL を **他ブラウザ（Safari/Firefox）** でも目視確認。失敗時はログを Claude へ。
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
- [x] **P4 WebGL/WASM/CPU 追従** — WebGL E2E PASS・onnx-proto→protobufjs・emscripten 手順整備 ✅（WASM 実ビルドは人手 TODO）
  - 計画書: [2026-06-17-p4-webgl-wasm-deps.md](superpowers/plans/2026-06-17-p4-webgl-wasm-deps.md)（全 Task 完了）
- [x] **P5 ドキュメント・配布整備** — README/CONTRIBUTING/architecture・uv 移行・npm 配布構成整合 ✅
  - 計画書: [2026-06-18-p5-docs-distribution.md](superpowers/plans/2026-06-18-p5-docs-distribution.md)（全 Task 完了）

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
