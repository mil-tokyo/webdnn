# モダナイゼーション記録（2026 / 完了済みアーカイブ）

このディレクトリは **2026 年に実施したコードベース刷新（P0–P5）の歴史的記録**である。
作業は完了しており、ここにあるのは当時の計画・進捗・実測ログ。**現行コードの使い方・開発手順
ではない**（それらは下記「現行ドキュメント」を参照）。

## 何をしたか（要約）

2021 年頃のスタックで止まっていた WebDNN v2 を現行ブラウザ・現行ツールチェーンへ刷新した。

- ツールチェーン: yarn→**npm**、TypeScript 5、ESLint 9 (flat)、Prettier 3、webpack→**Vite**
- テスト基盤: **vitest** ユニット + **Playwright** E2E + GitHub Actions CI（GPU なし）
- **WebGPU**: 廃止された GLSL+SPIR-V(glslang) を **WGSL + 現行 API** へ全面移行
- 依存: メンテ終了の `onnx-proto` を **protobufjs 生成バインディング**へ置換
- Python: `setup.py`→**`pyproject.toml`（uv）**
- 結果: **CPU / WebGPU / WebGL / WASM の 4 バックエンドすべてが実機 4 ブラウザで動作確認済み**

## このディレクトリの中身

- [modernization-plan.md](modernization-plan.md) — 全 6 フェーズの上位計画（承認版）
- [modernization-status.md](modernization-status.md) — 進捗トラッカーの最終状態（完了記録）
- [baseline.md](baseline.md) — 移行前ベースラインと各フェーズの実測ログ
- [plans/](plans/) — フェーズ別の詳細実装計画（P0+P1 / P2 / P3 / P4 / P5）

## 現行ドキュメント（このアーカイブではなくこちらを参照）

- プロジェクト概要・開発手順: リポジトリ root の [CLAUDE.md](../../CLAUDE.md) / [README.md](../../README.md) / [CONTRIBUTING.md](../../CONTRIBUTING.md)
- アーキテクチャ: [../architecture.md](../architecture.md)
- テスト: [../testing.md](../testing.md)
- WASM ビルド（emscripten）: [../emscripten-setup.md](../emscripten-setup.md)
