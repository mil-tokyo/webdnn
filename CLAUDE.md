# CLAUDE.md

このファイルは Claude Code が本リポジトリで作業する際に毎セッション読み込まれる。

## プロジェクト概要

WebDNN v2.0.0-alpha — ブラウザ向け ONNX 推論ランタイム。Python 前処理なしで ONNX を
ブラウザに直接ロードして推論する。バックエンドは CPU / WebAssembly / WebGL(1/2) / WebGPU の4種で、
いずれも最新ブラウザで動作する（実機4ブラウザで確認済み）。

- ランタイム本体: `src/descriptor_runner/`（TypeScript）
  - `backend/{cpu,wasm,webgl,webgpu}/` — バックエンド実装
  - `operators/{cpu,wasm,webgl,webgpu}/` — 演算子
  - `core/` — モデルロード・テンソルデコード・ランナー
  - `onnx/` — ONNX protobuf バインディング（protobufjs 生成、`npm run gen:onnx` で再生成）
  - `separateBuild/` — バックエンド別の分割ビルドエントリ
- WebGPU シェーダ: `src/shader/webgpu/`（**WGSL**。`shader:webgpu` で `operators/webgpu/shaders.ts` を生成）
- WASM カーネル(C++): `src/shader/wasm/`（emscripten ビルド）
- Python（モデル最適化）: `src/graph_transpiler/`
- テスト: `test/unit/`（vitest）, `test/e2e/`（Playwright）, `test/model_test/runner/`（ブラウザ目視）
- デモ: `example/`

詳細は [docs/architecture.md](docs/architecture.md) を参照。

## 開発コマンド

```bash
npm install          # 依存インストール（パッケージマネージャは npm）
npm run typecheck    # 型チェック（tsc --noEmit）
npm run lint         # ESLint 9 (flat config)
npm run format       # Prettier 3
npm test             # ユニットテスト（vitest, GPU/DOM 不要）
npm run build        # Vite ビルド（dist に 9 バンドル + 型定義）
npm run build:all    # シェーダ生成 + ビルド（emscripten 非依存）
npm run server       # ローカル HTTP サーバ（ブラウザ目視テスト用）
```

テスト・ビルドの詳細手順:
- テスト3層（vitest / Playwright / ブラウザ目視）と実行方法 → [docs/testing.md](docs/testing.md)
- WASM バックエンドのビルド（emscripten 導入） → [docs/emscripten-setup.md](docs/emscripten-setup.md)
- E2E フィクスチャ生成は `npm run fixtures`（uv 環境、`test/fixtures/`）

## 規約・構成上の前提

- **パッケージマネージャ: npm**（`package-lock.json`）。
- **ビルド: Vite**（`scripts/build.mjs` が駆動）。
- **WebGPU: WGSL**（現行 API）。
- **ONNX パース: protobufjs 生成バインディング**（`src/descriptor_runner/onnx/`、`npm run gen:onnx`）。
- **Python: uv 環境**（`pyproject.toml`）。
- **生成物スタブ**: `scripts/ensure-generated-stubs.mjs` が emscripten/シェーダ未導入環境でも
  `worker.ts`/`shaders.ts` のスタブを供給し、typecheck/build を成立させる（WASM はオプトイン）。
- 対象ブラウザ: Chrome / Edge / Safari / Firefox の最新版。
- コミット／プッシュ、npm publish / PyPI 公開はユーザーの指示があったときのみ。

## 履歴

2026 年に実施した大規模刷新（P0–P5）の計画・進捗・実測ログは
[docs/modernization/](docs/modernization/) にアーカイブしている（完了済み・歴史的記録）。
