# Neural Style Transfer

以下のNeural Style Transferモデル（on chainer）をWebGPUで動かすサンプル

- [yusuketomoto/chainer-fast-neuralstyle](https://github.com/yusuketomoto/chainer-fast-neuralstyle)
- [gafr/chainer-fast-neuralstyle-models](https://github.com/gafr/chainer-fast-neuralstyle-models)

## 手順


1. `../../resources/` に [gafr/chainer-fast-neuralstyle-models](https://github.com/gafr/chainer-fast-neuralstyle-models) をクローンする。
    モデルデータが入っており200MB程度の容量があるため注意。
    
    ```bash
    $ cd ../../
    $ git clone https://github.com/gafr/chainer-fast-neuralstyle-models
    ```
    
2.  モデルを変換する

    ```bash
    $ python convert.py 
    ```
    
3.  まだ。

