# モダナイゼーション進捗ステータス（living document）

> このファイルは刷新作業の **現在地と「次の一手」の単一の真実**。
> 1ステップでも進めたら必ずここを更新すること。CLAUDE.md からの入口。

最終更新: 2026-06-17

## 作業ブランチ

- 刷新作業は **`modernization` ブランチ** で行う（`master` には完成フェーズのみ取り込む）。
- 実行方式: Subagent-Driven（タスクごとに実装サブエージェント + spec/品質レビュー）。

## 現在地

- **現在フェーズ: Phase 1（ツールチェーン刷新）— 進行中**
- 完了: P0 ベースライン確立（[docs/baseline.md](baseline.md)、commit 3290804d）。
- 実装中の計画書: [docs/superpowers/plans/2026-06-17-p0-p1-baseline-and-toolchain.md](superpowers/plans/2026-06-17-p0-p1-baseline-and-toolchain.md)

### P0 で判明した重要事項（後続フェーズで効く）
- `@webgpu/glslang` による `shader:webgpu`（GLSL→SPIR-V）は**ビルド自体は現状でも成功**する（実行時にブラウザで動かない問題は別）。
- webpack ビルドは Node 26 で `NODE_OPTIONS=--openssl-legacy-provider` が必要（Vite 移行で解消見込み）。
- 全 webpack ビルドの失敗根因は、emscripten 未導入で `operators/wasm/worker/worker.ts` が生成されないこと。emscripten はシステムグローバル導入が必要（P4 / 人手）。
- 実行環境に yarn・emcc は未インストール。Python は `python3` のみ（`python` 名なし）。

## 👉 次の一手（NEXT STEP）

**Phase 0+1 計画の Task 2「yarn → npm 統一」から続行する。**
- 以降 Task 3〜8（Node 固定 → @webgpu/types → TS5 → ESLint9 → Vite → 統合検証）を順に実装。
- `python` 名が無い環境のため、Python を呼ぶ npm script は `python3` 前提に直す必要がある（Task 7 周辺で考慮）。

## フェーズ一覧と進捗

上位計画: [docs/modernization-plan.md](modernization-plan.md)

- [ ] **P0 ベースライン確立** — 現状の動作状況を `docs/baseline.md` に記録
- [ ] **P1 ツールチェーン刷新** — npm / TS5 / ESLint9 flat / Vite / `@webgpu/types` 更新
  - 計画書: [2026-06-17-p0-p1-baseline-and-toolchain.md](superpowers/plans/2026-06-17-p0-p1-baseline-and-toolchain.md)
- [ ] **P2 自動テスト基盤** — vitest + 実機Playwright + ブラウザ目視ランナー + CI（GPUなし）
  - 計画書: 未作成（P1 マージ後に作成）
- [ ] **P3 WebGPU WGSL 移行** — 12 GLSL→WGSL・現行 API 化・glslang 除去
  - 計画書: 未作成（P2 マージ後に作成）
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
