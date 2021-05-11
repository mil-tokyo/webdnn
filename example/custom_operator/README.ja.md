# カスタムオペレータの実装例

ONNX仕様に存在しないカスタムオペレータを実装し、動作させるサンプル。

入力を2倍にする`Twice`という名前のカスタムオペレータを含むモデルを作成し、WebDNN上で実行する。

Pythonスクリプトの実行には、PyTorch (`>=1.7`)が必要。

# 操作手順
## カスタムオペレータを含むONNXモデルを生成
```
python make_model.py
```

## カスタムオペレータの実装を設置

カスタムオペレータの実装である`twice.ts`を`<repository_root>/src\descriptor_runner\operators\cpu\operators\custom\twice.ts`にコピー。

## カスタムオペレータを含むオペレータセットのビルド

```
python -m webdnn.optimize_model output/model.onnx output
```

出力ファイル`model-{cpu,wasm,webgl}.onnx`, `op-{cpu,wasm,webgl}.js`, `weight-{cpu,wasm,webgl}-0.bin`が生成される。`op-{cpu,wasm,webgl}.js`に標準オペレータおよびカスタムオペレータの実装が含まれる。`model.onnx`はもはや必要ない。

## Webブラウザ上での実行

repository rootにて

```
yarn server
```

を実行。この状態で、Webブラウザで[http://localhost:8080/example/custom_operator/](http://localhost:8080/example/custom_operator/)を開く。

このサンプルでは、カスタムオペレータはCPU上で動作する実装である。GPU上で動作する実装が存在する標準オペレータは、GPU上で動作し、カスタムオペレータの実行前後で自動的にテンソルデータがCPU/GPU間で転送される。
