# Benchmark

WebDNNの実行速度測定ベンチマークです。
比較対象は[Keras.js](https://github.com/transcranial/keras-js)、ベンチマークモデルとしてResNet50を使用します。

## セットアップ

### WebDNNのモデル変換

ChainerのResNet50モデルを使用する

```shell
$ python ./convert_webdnn.py
```

### Keras.jsのモデル変換

```shell
$ ./convert_kerasjs.sh
```

### 実行

`index.html` へアクセス。コンソール画面を開いた状態で `RUN` ボタンをクリック。
