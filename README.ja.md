# WebDNN

[English](README.md)

WebDNN version 2のα版です。WebDNN 1.xとの大きな違いは、入力としてONNX形式のモデルのみを受け付ける点です。Pythonによる前処理なしで、ONNXモデルを直接Webブラウザで読み込むことが可能です。さらに、オフラインでのモデル最適化を行うことも可能です。

[Version 1.x](https://github.com/mil-tokyo/webdnn/tree/v1.2.11)

# 対応バックエンド(高速化技術)

モダンブラウザのほとんどで、WebGLが使用可能。

- WebGPU
  - Chrome Canary搭載版。
  - iOS13に搭載のWebGPUは廃止予定のWSL言語によるシェーダを必要とするため非対応。
- WebGL
  - WebGL2が使用可能な場合は使用する。WebGL1のみ対応のSafariにも対応。
- WebAssembly

# 開発環境セットアップ

node.js 14, python 3.6以降, emscripten 2.0以降が動作する環境が必要です。

```
yarn
python setup.py develop
```

# ビルド
```
yarn build:all
```

ビルド成果物
- `dist/webdnn.js`
  - 最適化されていないONNXモデルを読み込むことができるライブラリ
- `dist/webdnn-core.js`
  - WebDNNにより最適化されたモデルを読み込むことができるライブラリ

# 基本的な使い方

`dist/webdnn.js`を`<script>`タグでロードすることで、グローバルに`WebDNN`オブジェクトが追加される。ONNXモデル`model_directory/model.onnx`が存在すると仮定し、形状`[1, 2]`のテンソルを入力として実行する。

```javascript
const runner = await WebDNN.load("model_directory/");
const inputDataArray = new Float32Array([5.1, -2.3]);
const inputTensor = new WebDNN.CPUTensor([1, 2], "float32", inputDataArray);
const [outputTensor] = await runner.run([inputTensor]);

console.log(outputTensor.data);  // Float32Array
```

動作する最小限の完全なコードは`example/minimum`を参照。

# テスト

テスト対象のONNXモデルおよび、入出力テンソルの生成

```
pip install -r requirements.test.txt
python test/model_test/make_models.py
```

Webブラウザ上での実行

```
yarn server
```

Webブラウザで<http://localhost:8080/test/model_test/runner/standard.html>を開き、テストしたいバックエンドにチェックを入れ、Testボタンをクリックすることでテストが実行される。

モデルの最適化を含めたテストを行う場合は、

```
python test/model_test/make_models.py --optimize
```

<http://localhost:8080/test/model_test/runner/optimized.html>

を使用する。ただし、`make_models.py`の実行時間が長くかかる。
