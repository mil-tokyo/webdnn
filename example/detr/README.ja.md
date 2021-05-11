# DETRによる物体検出

Pythonスクリプトの実行には、PyTorch (`>=1.7`)が必要。

# 操作手順
## PyTorchモデルをONNXモデルに変換
```
python conversion.py
```

## Webブラウザ上での実行

repository rootにて

```
yarn server
```

を実行。この状態で、Webブラウザで[http://localhost:8080/example/detr/](http://localhost:8080/example/detr/)を開く。
