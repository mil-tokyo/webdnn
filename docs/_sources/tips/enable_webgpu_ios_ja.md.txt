# WebGPUをiOS 11で有効にする方法
[English](../enable_webgpu_ios.html)

iOS 11に搭載のWebブラウザSafariには、実験的機能としてWebGPUが搭載されています。WebGPUにより、WebDNNの動作は大幅に高速化されます。
初期設定ではWebGPUは無効になっているため、このページでは、WebGPUを有効にする方法を説明します。

1. 設定を開き、Safariをタップ

    <img src="../_static/tips/webgpu_ios_1_ja.png" width="320px" alt="Safari">

2. 詳細をタップ

    <img src="../_static/tips/webgpu_ios_2_ja.png" width="320px" alt="Advanced">

3. Experimental Featuresをタップ

    <img src="../_static/tips/webgpu_ios_3_ja.png" width="320px" alt="Experimental Features">

4. WebGPUをONにする

    <img src="../_static/tips/webgpu_ios_4_ja.png" width="320px" alt="WebGPU">

5. Safariが起動している場合、一旦終了する

    <img src="../_static/tips/webgpu_ios_5.png" width="320px" alt="Close Safari">

    (ホームボタンをダブルクリック、Safariの画面を上にスワイプ)

これにより、SafariでWebGPUが利用できるようになります。

注意：WebGPUは実験的機能であり、ブラウザの動作を不安定にする可能性があります。WebGPUを使用したい場合以外は無効化しておくことが望ましいです。
