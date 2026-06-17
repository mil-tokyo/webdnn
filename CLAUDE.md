# CLAUDE.md

このファイルは Claude Code が本リポジトリで作業する際に毎セッション読み込まれる。

## ⚠️ 最初に読むこと — 刷新作業が進行中

このコードベースは現在、**大規模なモダナイゼーション（刷新）作業の途中**にある。
新しいセッションを始めたら、コードに触れる前に必ず次を確認すること:

1. **[docs/modernization-status.md](docs/modernization-status.md)** — 現在地と「次の一手」の単一の真実（living document）。**まずこれを読む。**
2. **[docs/modernization-plan.md](docs/modernization-plan.md)** — 全6フェーズの上位計画（承認済み）。
3. **[docs/superpowers/plans/](docs/superpowers/plans/)** — フェーズ別の詳細実装計画（チェックボックス形式）。

作業を1ステップでも進めたら、**`docs/modernization-status.md` の現在フェーズ・チェック状況・次の一手を更新する**こと。
これを怠ると次のセッションが文脈を見失う。

## プロジェクト概要

WebDNN v2.0.0-alpha — ブラウザ向け ONNX 推論ランタイム。Python 前処理なしで ONNX を
ブラウザに直接ロードして推論する。バックエンドは CPU / WebAssembly / WebGL(1/2) / WebGPU の4種。

- ランタイム本体: `src/descriptor_runner/`（TypeScript）
  - `backend/{cpu,wasm,webgl,webgpu}/` — バックエンド実装
  - `operators/{cpu,wasm,webgl,webgpu}/` — 演算子
  - `core/` — モデルロード・テンソルデコード・ランナー
  - `separateBuild/` — バックエンド別の分割ビルドエントリ
- WebGPU シェーダ: `src/shader/webgpu/`
- WASM カーネル(C++): `src/shader/wasm/`
- Python（モデル最適化）: `src/graph_transpiler/`
- テスト: `test/model_test/`（ブラウザ実行）
- デモ: `example/`

## 刷新で確定した拘束（binding decisions）

これらは [docs/modernization-plan.md](docs/modernization-plan.md) §2.1 で確定済み。逆行させないこと:

- **パッケージマネージャ: npm**（yarn は廃止。`package-lock.json` を使う）
- **Python: uv 環境**（`pyproject.toml` + `uv.lock`。`setup.py` は廃止予定）
- **ビルド: Vite**（webpack は廃止予定。`scripts/build.mjs` が駆動）
- **WebGPU: WGSL 必須**（旧 GLSL+SPIR-V / glslang は廃止。現行 API へ移行）
- **onnx-proto は廃止**し protobufjs 生成バインディングへ移行（P4）
- **GPU テストは CI で実行しない**。実機 Playwright + 全ブラウザ目視で担保
- **emscripten はシステムグローバル導入**（ワークツリー単位では入れない／自動インストールしない）
- **npm publish / PyPI 公開は手動**（Claude は実行しない）
- 対象ブラウザ: Chrome / Edge / Safari / Firefox の最新版

## 開発コマンド（移行中のため流動的。最新は package.json と status を参照）

```bash
npm install          # 依存インストール（yarn は使わない）
npm run typecheck    # 型チェック（WebGPU の既知エラーは @ts-expect-error + TODO(P3) で切り分け中）
npm run lint         # ESLint 9 flat config
npm run build        # Vite ビルド
npm run test         # テスト（P2 で整備中）
npm run server       # ローカル HTTP サーバ（ブラウザ目視テスト用）
```

## 作業の進め方

- 実装は各フェーズの計画（`docs/superpowers/plans/`）に沿って、TDD・小さなコミットで進める。
- フェーズをまたぐ作業や新しい設計判断が必要になったら、勝手に進めず計画／status を更新してから着手する。
- コミット／プッシュはユーザーから指示があったときのみ行う。
- 実 GPU・emscripten 導入・publish など Claude が実行できない作業は status の「人手が必要」に記録し、ユーザーへ依頼する。
