# WebDNN コードベース刷新計画

作成日: 2026-06-17
対象: WebDNN v2.0.0-alpha（ブラウザ向け ONNX 推論ランタイム）
ステータス: レビュー待ち（ドラフト）

---

## 0. この文書の目的

現状の WebDNN コードベースは 2021 年前後の技術スタックで止まっており、特に
**WebGPU バックエンドは現行のどのブラウザでも動作しない**状態にある。本計画は、
機能追加は行わず、以下を達成するための作業を依存関係順に整理したものである。

- 現行ブラウザ（Chrome / Edge / Safari / Firefox の最新版）で実際に推論が動く状態にする
- WebGPU / WebGL の規格変更に追従する（行数が多くても実施する）
- 継続開発しやすい保守基盤（CI・自動テスト・型チェック・Lint）を整える
- ビルド／ツールチェーンを現代的構成へ移行する

各フェーズには「**Claude が自動で実施できる範囲**」と「**人間の確認・操作が必要な範囲**」
を明記する。後者は主に、実 GPU を伴う複数ブラウザでの最終動作確認と、npm publish などの
資格情報を要する操作である。

---

## 1. 現状分析（2026-06-17 時点）

### 1.1 アーキテクチャ概要

- **目的**: ONNX モデルをブラウザに直接ロードし、Python 前処理なしで推論する。
- **入力**: ONNX（`onnx-proto` でパース）。オフライン最適化版もある（`webdnn-core.js`）。
- **バックエンド**: CPU / WebAssembly / WebGL(1/2) / WebGPU の 4 種。
- **コード規模**: TypeScript 約 18,200 行（137 ファイル）、Python 25 ファイル、
  C++ 6 ファイル（WASM カーネル）、GLSL 12 ファイル（WebGPU シェーダ）。
- **主要ディレクトリ**:
  - `src/descriptor_runner/` — ランタイム本体（TS）
    - `backend/{cpu,wasm,webgl,webgpu}/` — 各バックエンドのコンテキスト実装
    - `operators/{cpu,wasm,webgl,webgpu}/` — 演算子実装（CPU 32 / WebGL 24 / WASM 9 / WebGPU 6）
    - `core/` — モデルロード・テンソルデコード・ランナー
    - `separateBuild/` — バックエンド別の分割ビルドエントリ
  - `src/shader/webgpu/` — GLSL シェーダ群とコンパイルスクリプト（`compile.js`）
  - `src/shader/wasm/` — C++ カーネルと emscripten ビルド（`compile.py`）
  - `src/graph_transpiler/` — Python 側のモデル最適化・テンソル書き出し
  - `test/model_test/` — ブラウザ HTML によるモデル単位テスト
  - `example/` — resnet / detr / mobilenet などのデモ

### 1.2 「古い」と判断した具体的根拠

| 領域 | 現状 | 問題 |
|------|------|------|
| WebGPU シェーダ | GLSL `#version 450` → `@webgpu/glslang` で SPIR-V 化 | **現行 WebGPU は WGSL のみ**。SPIR-V/GLSL 経路は削除済み。`@webgpu/glslang` はメンテ終了 |
| WebGPU API | `createComputePipeline({computeStage})`, `passEncoder.dispatch()`, `passEncoder.endPass()` | すべて旧 API。現行は `compute` / `dispatchWorkgroups()` / `end()`。**そのままでは例外で停止** |
| WebGPU 型 | `@webgpu/types@^0.0.45` | 現行は 0.1.x 系。型と実装が乖離 |
| TypeScript | `4.2.3` / `target es2017` | 現行は 5.x。`moduleResolution` など設定が古い |
| Lint | ESLint `7.x` + `.eslintrc.json` | 現行は 9.x の flat config（`eslint.config.js`） |
| ビルド | webpack 5 早期 + `ts-loader` + 9 個の個別 config | 設定が冗長。Vite/esbuild で大幅簡素化可能 |
| パッケージ | `onnx-proto@4.0.4`, `pako@2`, yarn classic（`yarn.lock`） | onnx-proto はメンテ終了。npm へ統一し代替へ移行する |
| Python | `python >= 3.6`, `setup.py develop` | 3.6 は EOL。uv 環境 + `pyproject.toml` へ移行する |
| WASM | emscripten 2.0 前提、`-std=c++11`、eigen 3.3.9 を実行時 DL | ビルド再現性が低い（バージョン固定なし） |
| テスト | `npm test` は `exit 1`。ブラウザ手動 HTML のみ | **自動テスト・CI が一切ない** |
| CI | `.github/` なし | 回帰検知の仕組みがない |

### 1.3 結論

WebGPU バックエンドは事実上の全面書き換えが必要。その他は「動かす」より
「**安全に変更し続けられる土台を先に作る**」ことが最優先。よって、ツールチェーンと
自動テスト基盤を先行させ、その保護下でバックエンド改修を行う順序とする。

---

## 2. 全体方針と作業順序

### 2.1 確定した方針（レビュー反映済み）

- **パッケージマネージャ**: yarn をやめ **npm** に統一する（`package-lock.json`）。
- **Python**: **uv** 環境へ移行（`pyproject.toml` + `uv.lock`、`setup.py` は廃止）。
- **GPU テスト**: **CI では実 GPU テストを行わない**（CI は lint / typecheck / ユニット /
  ビルドのみ）。GPU 系は次の二段構えで担保する。
  1. **ローカル実機（Windows / Mac）での Playwright 自動チェック** — 実 GPU 上で
     WebGL / WebGPU 推論を起動し CPU 参照と数値比較。開発者が手元で実行する。
  2. **全対象ブラウザでの目視確認** — `npm` 起動の HTTP サーバの URL を各ブラウザで
     開くとテストが走り、OK 表示を目視確認する。失敗時はそのログを Claude に貼り戻す。
- **onnx-proto**: メンテ終了のため **代替へ移行**。推奨は `protobufjs` で公式
  `onnx.proto` から静的バインディングを生成・ベンダリングする方式（onnxruntime-web と
  同手法、`ModelProto.decode` / `TensorProto.DataType` の API を維持できる）。
- **emscripten**: 容量が大きいためワークツリー単位では入れず、**システムグローバルに
  導入する手順を文書で提供**する（自動インストールはしない）。
- **npm publish / PyPI 公開**: 手動運用（Claude は実行しない）。

### 2.2 作業順序

依存関係に基づき、後段の改修が前段の安全網（型チェック・Lint・CI・テスト）の
保護下で行われるよう順序付ける。

```
P0 ベースライン確立
   └─ P1 ツールチェーン刷新 ──┬─ P2 自動テスト基盤
                              │        └─ P3 WebGPU WGSL 移行 ─┐
                              │        └─ P4 WebGL/WASM/CPU 追従 ┼─ P5 ドキュメント・配布
                              └──────────────────────────────────┘
```

各フェーズは独立した PR（またはブランチ）として完結させ、レビュー・マージ可能にする。

---

## 3. フェーズ別計画

### Phase 0 — ベースライン確立（現状把握）

**目的**: 改修前の「動く／動かない」を実証的に記録し、回帰判定の基準点を作る。

**Claude が自動で実施**
- 依存セットアップ（既存 `yarn` / `python setup.py develop` / emscripten 確認）を試行し、
  成功・失敗をログ化（移行前の現状把握のため、この時点では既存ツールのまま動かす）。
- 現行ビルド（`yarn build:all` 相当）を試行し、どのステップが通り、どこで失敗するかを記録。
- 各バックエンドの「期待挙動」と「現状の壊れ方」を `docs/baseline.md` に整理。
- 既存テスト（`test/model_test`）を起動できる状態にし、CPU バックエンドで通る
  ケースを確認（GPU 系は次フェーズ以降）。

**人間の確認が必要**
- emscripten / Python 環境のインストール可否（マシン依存）。
- 実ブラウザでの現状スクリーンショット（任意、参考用）。

**成果物**: `docs/baseline.md`（現状の動作状況マトリクス）。

**完了条件**: 「何が動き、何が壊れているか」が文書化され、以降の回帰判定に使える。

---

### Phase 1 — ツールチェーン刷新（土台）

**目的**: 以降の全改修を型チェック・Lint で守れるよう、開発基盤を現代化する。

**Claude が自動で実施**
- **パッケージマネージャを npm に統一**: `yarn.lock` を廃止し `package-lock.json` を生成。
  全 scripts・ドキュメントを `npm run` ベースに統一。
- Node を最新 LTS 前提に更新（`.nvmrc` / `engines` 追記）。
- TypeScript を 5.x に更新。`tsconfig.json` を見直し
  （`target` 引き上げ、`moduleResolution: bundler` 等、`strict` 維持）。
- `@webgpu/types` を 0.1.x 系へ更新（P3 の前提）。これにより旧 API 呼び出しが
  **型エラーとして可視化**され、P3 の作業範囲が型で確定する。
- ESLint を 9.x の flat config（`eslint.config.js`）へ移行。prettier 連携を維持。
- ビルドを **Vite（library mode）/ esbuild** へ移行。9 個の webpack config を
  単一設定 + エントリ定義に集約（`webdnn.js` / `webdnn-core.js` / バックエンド別分割を維持）。
- `package.json` の scripts を整理（`build` / `dev` / `lint` / `typecheck` / `test`）。
- 依存のメジャー更新（`pako` 等）。`onnx-proto` の代替移行は P4 で実施する
  （本フェーズでは型更新と並行して影響範囲だけ調査）。

**人間の確認が必要**
- なし（方針は §2.1 で確定済み）。npm への移行・lockfile 再生成は Claude が実施する。

**成果物**: 新 `tsconfig.json` / `eslint.config.js` / `vite.config.ts` / `package-lock.json` /
更新版 `package.json`。

**完了条件**: `npm run typecheck` と `npm run lint` が通り（P3 で直す予定の WebGPU 型エラーは
明示的に切り分け）、`npm run build` で従来同等の dist が生成される。

---

### Phase 2 — 自動テスト基盤

**目的**: 回帰検証の網を 3 層で整える。**CI は GPU を使わない**（lint / typecheck /
ユニット / ビルドのみ）。GPU 系はローカル実機の自動チェックと、全ブラウザの目視確認で担保する。

**第 1 層 — CI（GPU 不要・常時実行）／ Claude が自動で実施**
- **CPU ユニットテスト（vitest）**: 演算子のリファレンス実装・テンソルデコード・
  モデルロード・math/util を Node 上でテスト。GPU 不要で最も価値が高く、CI で常時回せる。
- **GitHub Actions CI**: `lint` + `typecheck` + ユニットテスト + `build` を PR ごとに実行。
  **GPU テストは CI に含めない**。

**第 2 層 — ローカル実機の Playwright 自動チェック（Windows / Mac）／ Claude が仕組みを構築**
- 開発者の実機で `npx playwright test` 等を実行し、実 GPU 上のブラウザを起動して
  WebGL / WebGPU の推論を走らせ、**CPU 参照と数値比較**して自動で OK/NG 判定する。
- 起動には `npm` の HTTP サーバ（既存 `npm run server` を整備）を利用。
- Claude はこの Playwright 構成・比較ロジック・実行手順（`docs/testing.md`）を用意する。
  実行自体は実 GPU が要るため開発者の手元で行う（CI では走らせない）。

**第 3 層 — 全対象ブラウザでの目視確認 / Claude が仕組みを構築**
- `npm` で起動する HTTP サーバの URL（既存 `test/model_test/runner/*.html` を刷新）を
  各対象ブラウザ（Chrome / Edge / Safari / Firefox）で開くと全ケースが走り、
  **「OK」表示を目視確認**できるテストランナーを整備する。
- 失敗時は画面のログを Claude に貼り戻して原因調査に使う運用を前提とする。
- Playwright（第 2 層）でカバーできない手動・実機ブラウザを補完する。

**テストフィクスチャの固定化（共通基盤）／ Claude が自動で実施**
- `test/model_test/make_models.py` が生成する ONNX と期待出力を、**uv 管理の固定環境**
  （torch / onnx / onnxruntime を `pyproject.toml` で pin）で再現可能にする。
- 軽量フィクスチャはコミット、大きいものは生成手順を文書化。第 1〜3 層すべてが
  同一フィクスチャを参照する。

**人間の確認が必要**
- 実機（Windows / Mac）での Playwright 実行（第 2 層）。
- 全対象ブラウザでの目視確認と、失敗時ログの共有（第 3 層）。

**成果物**: `vitest` 設定 + ユニットテスト群、`playwright` 設定 + 実機自動チェック、
刷新版ブラウザテストランナー、`.github/workflows/ci.yml`（GPU なし）、`docs/testing.md`。

**完了条件**: PR ごとに CI で lint/typecheck/unit/build が緑になる。実機 Playwright と
ブラウザ目視ランナーが整備され、各バックエンドの合否を判定できる。

---

### Phase 3 — WebGPU バックエンドの WGSL 移行（規格追従の本丸）

**目的**: 現行 WebGPU 規格に完全追従し、最新ブラウザで WebGPU 推論を復活させる。
**本フェーズが行数最大かつ最重要。** P1（型更新）と P2（テスト）の保護下で行う。

**Claude が自動で実施**
- **シェーダ言語の移行**: `src/shader/webgpu/shadersources/standard/*.glsl`（12 本）を
  すべて **WGSL** へ書き換え。`@webgpu/glslang`（SPIR-V 化）を依存から除去。
  - 対象例: `binary_elementwise_add`, `binary_broadcast_add_{0..4}d`,
    `conv_im2col`, `conv_matmul`, `conv_bias`, `conv_transpose` ほか。
  - `std430` バッファ宣言 → WGSL の `@group/@binding var<storage>`、
    `gl_GlobalInvocationID` → `@builtin(global_invocation_id)`、
    `local_size_x` → `@workgroup_size` へ対応付け。
- **シェーダ生成パイプラインの刷新**: `src/shader/webgpu/compile.js` を、WGSL を
  そのまま文字列として `shaders.ts` に埋め込む形へ変更（SPIR-V バイナリ生成を廃止）。
- **API の現行化**（`backend/webgpu/webgpuContextImpl.ts` ほか）:
  - `createComputePipeline({ computeStage })` → `{ layout, compute: { module, entryPoint } }`
  - `passEncoder.dispatch()` → `dispatchWorkgroups()`
  - `passEncoder.endPass()` → `end()`
  - `requestAdapter` / `requestDevice` のエラーハンドリング・feature/limits の現行化
  - バッファマッピング（`mapAsync` / `getMappedRange` / `unmap`）と
    `GPUBufferUsage` フラグの見直し（`webgpuTensorImpl.ts` / `webgpuMetaBuffer.ts`）。
  - bind group / pipeline layout の API 整合性確認。
- **回帰検証**: P2 第 2 層（実機 Playwright）と第 3 層（ブラウザ目視ランナー）で、
  各 WebGPU 演算子の出力を CPU 参照と数値比較。CI には GPU テストを含めない。

**人間の確認が必要**
- 実機（Windows / Mac）での Playwright 実行、および実 GPU を持つ
  Chrome / Edge（可能なら Safari / Firefox）での目視確認。失敗時はログを Claude に共有。

**成果物**: WGSL シェーダ群、刷新版 `compile`（→ WGSL 埋め込み）、
現行 API 準拠の WebGPU バックエンド、対応する E2E テスト。

**完了条件**: 最新 Chrome で `example/resnet` 等が WebGPU バックエンドで CPU と一致する
出力を返す。`@webgpu/glslang` 依存が完全に除去される。

---

### Phase 4 — WebGL / WASM / CPU の規格追従・依存更新

**目的**: 残りバックエンドを現行環境で確実に動かし、ビルド再現性を高める。

**Claude が自動で実施**
- **WebGL**: WebGL2 優先のコンテキスト取得・拡張機能取得の現行化、非推奨パターンや
  コンテキストロスト処理の確認。Safari の WebGL1 フォールバック経路の動作確認。
- **onnx-proto の代替移行**: メンテ終了の `onnx-proto` を除去し、`protobufjs` で
  公式 `onnx.proto` から静的バインディング（`onnx.js` / `onnx.d.ts`）を生成・ベンダリング
  する方式へ移行（onnxruntime-web と同手法）。現行の使用箇所
  （`core/runnerImpl.ts` の `onnx.ModelProto.decode` / `onnx.TensorProto.DataType`、
  `core/modelTransform.ts` の型、各 tensorDecoder）が API 互換で差し替わるようにし、
  パース層を薄く分離して将来の差し替えも容易にする。生成手順を `package.json` の
  スクリプト化（再現可能に）。
- **WASM / emscripten**: `compile.py`（uv 環境で実行）を、推奨 emscripten バージョンの
  明記と eigen の固定版取得（DL 失敗に強い再現手順）へ改善。`-std=c++11` の見直し。
  emscripten 本体は容量が大きいため **システムグローバル導入手順を `docs/` に記載**し、
  自動インストールはしない（ワークツリー単位では入れない）。ビルド済み成果物の検証を
  P2 のテストに接続。
- **CPU**: リファレンス実装はテストの基準なので、挙動を変えずにテストで固定。

**人間の確認が必要**
- Safari（WebGL1 経路）での実機確認。
- emscripten のシステムグローバル導入（手順は Claude が提供。容量が大きいため実行は手動）。

**成果物**: 更新版 WebGL バックエンド、`protobufjs` ベースの ONNX パース層、
再現性のある WASM ビルド手順 + emscripten 導入ドキュメント。

**完了条件**: WebGL / WASM / CPU が最新ブラウザ・固定ツールチェーンで E2E を通過する。

---

### Phase 5 — ドキュメント・配布整備

**目的**: 刷新後の状態に合わせてドキュメントと配布構成を整える。

**Claude が自動で実施**
- `README.md` / `README.ja.md` の更新（対応ブラウザ・WebGPU 状況・ビルド手順）。
- `CONTRIBUTING.md` の更新（新しい開発・テスト・ビルド手順）。
- アーキテクチャ概要ドキュメント（`docs/architecture.md`）。
- npm 配布構成の整備（`exports` フィールド、型定義 `.d.ts`、`files`、ESM/CJS 方針）。
- **Python の uv 移行**: `setup.py` を廃止し `pyproject.toml` + `uv.lock` に移行。
  開発手順を `uv sync` / `uv run` ベースに統一し、サポート Python 版を明確化。
- バージョニング方針（alpha からの位置づけ）の記述。
- emscripten システムグローバル導入手順（P4 で作成したもの）を開発ドキュメントへ集約。

**人間の確認が必要**
- 実際の `npm publish` / PyPI 公開（手動運用。資格情報が必要なため Claude は実行しない）。
- 対応ブラウザ表記の最終承認。

**成果物**: 更新ドキュメント一式、配布設定。

**完了条件**: 新規利用者が README どおりにビルド・実行でき、配布構成が現行で破綻しない。

---

## 4. Claude の自動実行範囲と限界（まとめ）

**自動でできること**
- すべてのコード・設定・シェーダの書き換え、依存更新、ビルド設定移行（npm / Vite / uv）。
- onnx-proto から protobufjs 生成バインディングへの移行。
- CPU ユニットテスト・CI（GPU なし）の新規作成と実行。
- 実機 Playwright 自動チェックと、ブラウザ目視テストランナーの**仕組みの構築**。
- ドキュメント整備（emscripten 導入手順を含む）。

**Claude だけでは保証できないこと（人間の確認・操作が必要）**
- 実機（Windows / Mac）での Playwright 実行と、実 GPU 上の複数ブラウザ
  （特に Safari / Firefox / WebGPU）での目視確認。失敗時はログを Claude に共有。
- emscripten のシステムグローバル導入（手順は Claude が提供、容量が大きいため実行は手動）。
- npm / PyPI への公開（手動運用）。

---

## 5. リスクと対策

| リスク | 影響 | 対策 |
|--------|------|------|
| WGSL 移行で数値挙動が変わる | 推論結果のずれ | P2 で CPU 参照との数値比較（実機 Playwright）を先に用意してから着手 |
| GPU テストが CI で回らない | 自動回帰検知の空白 | CI は GPU なしと割り切り、実機 Playwright + ブラウザ目視を必須運用にし `docs/testing.md` に明記 |
| `onnx-proto` の代替移行が破壊的 | 広範囲に影響 | protobufjs 生成で API 互換を保ち、パース層を分離して段階移行。テストで挙動固定 |
| emscripten / eigen のバージョン非固定 | ビルド再現性 | バージョンを固定し手順を CI 化 |
| ビルド移行（webpack→Vite）で出力差異 | 配布物の互換性 | P0 のベースライン出力と比較して検証 |
| 一度に変更しすぎる | レビュー困難・回帰原因特定困難 | フェーズ単位で PR を分割し、各 PR を緑にしてからマージ |

---

## 6. 想定する成果物一覧

- `docs/baseline.md` — 現状動作マトリクス（P0）
- `package-lock.json`（npm 化）/ `tsconfig.json` / `eslint.config.js` / `vite.config.ts` 更新（P1）
- `vitest` 設定 + ユニットテスト、実機 `playwright` 自動チェック、刷新版ブラウザ目視ランナー、
  `.github/workflows/ci.yml`（GPU なし）、`docs/testing.md`（P2）
- WGSL シェーダ群 + 刷新版シェーダ生成 + 現行 API 準拠 WebGPU バックエンド（P3）
- 更新版 WebGL バックエンド + protobufjs ベース ONNX パース層 +
  再現性のある WASM ビルド手順 + emscripten 導入ドキュメント（P4）
- 更新ドキュメント一式 + npm 配布設定 + `pyproject.toml`（uv）（P5）

---

## 7. レビュー観点（この計画への確認依頼）

確定済みの方針は §2.1 に集約した。残る確認点は以下。

1. フェーズ順序（土台 → テスト → WebGPU → 残り → ドキュメント）で問題ないか。
2. WebGPU の WGSL 全面移行を P3 に置く前提でよいか（P1/P2 を先に通す）。
3. ビルドの Vite 移行に異論はないか（既存 webpack 維持の選択肢も可）。
4. onnx-proto の代替として protobufjs 生成バインディング方式で問題ないか。
5. 対象ブラウザの範囲（Chrome / Edge / Safari / Firefox の最新版）の確定。
