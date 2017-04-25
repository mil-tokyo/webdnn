# PaintsChainer

[pfnet/PaintsChainer](https://github.com/pfnet/PaintsChainer)をWebGPUで動かすサンプル

## 手順


1. `../../resources/paints_chainer` に [学習済みモデル(60MB)](http://paintschainer.preferred.tech/downloads/unet_512_standard) をダウンロードする
    
2.  モデルを変換する

    ```bash
    $ python convert.py 
    ```
    
3.  ブラウザを起動して `index.html` へアクセス

