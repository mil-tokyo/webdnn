[![CircleCI](https://circleci.com/gh/mil-tokyo/webdnn.svg?style=svg)](https://circleci.com/gh/mil-tokyo/webdnn)

# WebDNN: Fastest DNN Execution Framework on Web Browser

**WebDNN** は深層学習モデル(DNN)をウェブブラウザ上で高速実行するためのオープンソースフレームワークです。

- [English README](https://github.com/mil-tokyo/webdnn/blob/master/README.md)
- [website](https://mil-tokyo.github.io/webdnn/index_ja.html)
- [document](https://mil-tokyo.github.io/webdnn/docs)

# Why is WebDNN needed?

DNNは様々なタスクについて顕著な成果をおさめていますが、アプリケーションへの実応用の上では、その計算コストが大きな問題となっています。
ハードウェアアクセラレーションによる解決方法では、煩雑な計算環境セットアップ手順やハードウェアの価格等が問題となり、ユーザーエンド端末に同様の環境を構築することは非常に困難です。

**WebDNN**はこの問題を解決するために作られた、ウェブブラウザを利用したインストールフリーなDNN実行環境です。
WebDNNにより、ウェブブラウザ上での実行を前提とした積極的な最適化が学習済みモデルに行われるため、
パラメータデータの配信サイズを小さく抑え、高速な実行が可能となります。

# Performance

- 比較対象: [Keras.js](https://github.com/transcranial/keras-js)
- 実行環境: 
    - Mac Book Pro early 2015
    - macOS 10.12.4 Sierra
    - Intel Core i5 2.7 GHz CPU
    - 16 GB Memory
    - Intel Iris Graphics 6100 GPU
    - Safari Technology Preview 30
- 測定内容: 画像識別モデルの一種, Vgg16[[2]](#2), Inception-v3[[4]](#4), ResNet50[[1]](#1)を使用。224x224(Inception-v3のみ299x299)の画像1枚の推論に要する時間を測定。

![Benchmark result with Keras.js](https://github.com/mil-tokyo/webdnn/blob/master/docs/misc/performance.png)

縦軸は画像1枚あたりの処理時間(対数スケール)を表しています。

WebDNNの実行バックエンドとしてWebGPUを使用した場合、Keras.jsよりも大幅な速度向上が達成されました。
また、WebAssembly実装によるCPU上での実行でも、Keras.jsのGPUモードと同等以上の速度が出ていることが分かります。
さらに、WebDNNに実装された最適化機構を用いる事でより一層の速度向上効果が得られています。

# Getting started in 30 seconds

ResNet50の学習済みKerasモデル[[3]](#3)を変換し、ブラウザ上で実行してみましょう。
まず、Kerasに付属しているResNet50の学習済みモデルを保存します。

```python
from keras.applications import resnet50
model = resnet50.ResNet50(include_top=True, weights='imagenet')
model.save("resnet50.h5")
```

次に、保存したモデルをCLIを用いて変換します。
モデルは **GraphDescriptor** という、WebDNNがモデルを実行するために必要な情報へと変換されます。
その際、モデルの最適化が同時に行われます。

```bash
python ./bin/convert_keras.py resnet50.h5 --input_shape '(1,224,224,3)' --out output
```

生成したDescriptorは、以下のJavaScriptコードで読み込み・実行ができます。

```js
let runner;

async function init() {
    // DNNを実行するための "DescriptorRunner" を初期化する
    runner = await WebDNN.load('./output');
}

async function run() {
    // 入力変数にデータをセット
    runner.getInputViews()[0].set(WebDNN.Image.getImageArray('./input_image.png'));
    
    // 実行
    await runner.run(); 

    // 結果を確認
    console.log('Output', WebDNN.Math.argmax(runner.getOutputViews()[0].toActual()));
}
```

他にもCaffemodel, Chainerモデルの変換にも対応しています。
詳しい使用例は[ドキュメント](https://mil-tokyo.github.io/webdnn/docs)を参照してください。

# セットアップ方法

[ドキュメント](https://mil-tokyo.github.io/webdnn/docs/tutorial/setup.html)を参照してください。

---

- <i id=1></i>[1] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. 2015. Deep Residual
    Learning for Image Recognition. In Proceedings of the Conference on Computer Vision and Pattern Recognition (CVPR). 
    [https://github.com/KaimingHe/deep-residual-networks](https://github.com/KaimingHe/deep-residual-networks)
- <i id=2></i>[2] Karen Simonyan and Andrew Zisserman. 2014. Very Deep Convolutional Networks for Large-Scale Image Recognition. 
    In Proceedings of the International Conference on Learning Representations (ICLR).
- <i id=3></i>[3] [Applications - Keras Documentation](https://keras.io/ja/applications/#resnet50)
- <i id=4></i>[4] Christian Szegedy, Vincent Vanhoucke, Sergey Ioffe, Jon Shlens, and Zbigniew Wojna. 2016.
    Rethinking the Inception Architecture for Computer Vision. In Proceedings of the Conference on Computer Vision and Pattern Recognition (CVPR).
