# WebDNN

[English](README.md)

WebDNN version 2 は、ニューラルネットワークの推論を Web ブラウザ上で直接実行します。WebDNN 1.x との大きな違いは、入力として ONNX 形式のモデルを受け付ける点です。Python による前処理なしで、ONNX モデルを直接 Web ブラウザに読み込めます。さらに、オフラインでのモデル最適化も可能です。

[Version 1.x](https://github.com/mil-tokyo/webdnn/tree/v1.2.11)

## 対応バックエンド（高速化技術）

- **WebGPU** — 現行の WGSL ベース実装。最新の Chrome / Edge（および WebGPU が有効な Safari / Firefox）で動作します。
- **WebGL** — WebGL2 が利用可能な場合は WebGL2 を使用し、WebGL1 にフォールバックします。
- **WebAssembly** — カーネルの emscripten ビルドが必要です。[docs/emscripten-setup.md](docs/emscripten-setup.md) を参照してください。

## 動作環境

- Node.js 20 以上（`.nvmrc` 参照）
- Python 3.10 以上（[uv](https://docs.astral.sh/uv/) 経由）— モデル最適化およびテスト用フィクスチャ生成時のみ必要
- emscripten 3.1 以上 — WebAssembly バックエンドをビルドする場合のみ必要

## セットアップ

```
npm install
uv sync            # Python のグラフトランスパイラ／最適化を使う場合のみ
```

## ビルド

```
npm run build:all
```

ビルド成果物（`dist/` 内）:

- `dist/webdnn.js` — UMD バンドル（グローバル `WebDNN`）。最適化されていない ONNX モデルを読み込めます
- `dist/webdnn-core.js` — WebDNN によりオフライン最適化された ONNX モデルを読み込めます
- `dist/op-*.js` — オペレータバンドル。実行時に動的ロードされます
- `dist/types/` — TypeScript 型定義

`build:all` は Vite ビルドの前に、WGSL シェーダ生成（`shader:webgpu`）とオペレータエントリ生成（`makeShaderList`、Python 3 が必要）を実行します。WebAssembly バックエンドは `build:all` ではビルドされません。ビルドには emscripten が必要です（[docs/emscripten-setup.md](docs/emscripten-setup.md) 参照）。

## 基本的な使い方

`dist/webdnn.js` を `<script>` タグでロードすると、グローバルに `WebDNN` オブジェクトが追加されます。ONNX モデル `model_directory/model.onnx` が存在すると仮定し、形状 `[1, 2]` のテンソルを入力として実行します。

```javascript
const runner = await WebDNN.load("model_directory/");
const inputDataArray = new Float32Array([5.1, -2.3]);
const inputTensor = new WebDNN.CPUTensor([1, 2], "float32", inputDataArray);
const [outputTensor] = await runner.run([inputTensor]);

console.log(outputTensor.data); // Float32Array
```

動作する最小限の完全なコードは `example/minimum` を参照してください。

## テスト

詳細なテストガイドは [docs/testing.md](docs/testing.md) を参照してください。

```
npm test            # ユニットテスト（vitest, GPU 不要）
npm run fixtures    # テスト用 ONNX フィクスチャ生成（uv, Python）
npm run test:e2e    # Playwright E2E（CPU / WebGPU / WebGL を自動検証）
npm run server      # 目視用ブラウザランナーの静的サーバ
```

目視用ブラウザランナーは <http://localhost:8080/test/model_test/runner/standard.html>
を開き、テストしたいバックエンドにチェックを入れて Test ボタンをクリックします。

`npm run fixtures` は、テストで使用する ONNX モデルおよび入出力テンソルを生成します。
（PyTorch に依存する従来の `test/model_test/make_models.py` は大規模モデル生成用として
残されており、標準フローには含まれません。）
