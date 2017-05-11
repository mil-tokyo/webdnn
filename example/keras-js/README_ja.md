# keras.jsでResNet50 inferenceを行うベンチマークサンプル

## セットアップ
kerasのセットアップ、resnet50モデルのダウンロード(100MB)、keras.js形式への変換が必要。

事前にpipで、`tensorflow`, `keras`パッケージのインストールが必要。
kerasは2.0系だと現状うまくいかない(https://github.com/transcranial/keras-js/issues/49)。`pip install keras==1.2.2`で解決。

モデル変換のためのステップ

```
./step1.sh
./step2.py
./step3.sh
```

## 実行
HTTPサーバでプロジェクトのルートディレクトリをホスティングし、index.htmlを開く。

"Load image"ボタン、"Setup"ボタンで準備をして、"inference"ボタンでDNNの計算を1回行い、その結果を表示する。"inference"ボタンは複数回使用可能。
