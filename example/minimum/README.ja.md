# 最小の実行サンプル

既存のONNXモデルをWebDNNを用いて実行する最小のサンプル。

このサンプルは、`model/model.onnx`を実行する。このモデルには、`Relu`オペレータだけが含まれている。`make_model.py`に生成方法が記載されている(PyTorchを使用)。

## Webブラウザ上での実行

repository rootにて

```
yarn server
```

を実行。この状態で、Webブラウザで[http://localhost:8080/example/minimum/](http://localhost:8080/example/minimum/)を開く。
