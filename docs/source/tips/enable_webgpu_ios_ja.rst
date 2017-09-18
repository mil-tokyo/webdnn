WebGPUをiOS 11で有効にする方法
==============================

- :doc:`macOSの場合 <./enable_webgpu_macos_ja>`
- :doc:`English <./enable_webgpu_ios>`

iOS 11に搭載のWebブラウザSafariには、実験的機能としてWebGPUが搭載されています。WebGPUにより、WebDNNの動作は大幅に高速化されます。
初期設定ではWebGPUは無効になっているため、このページでは、WebGPUを有効にする方法を説明します。

**1. 設定を開き、Safariをタップ**

    .. image:: ../_static/tips/webgpu_ios_1.png
        :width: 320px
        :alt: Safari

**2. 詳細をタップ**

    .. image:: ../_static/tips/webgpu_ios_2.png
        :width: 320px
        :alt: Advanced

**3. Experimental Featuresをタップ**

    .. image:: ../_static/tips/webgpu_ios_3.png
        :width: 320px
        :alt: Experimental Features

**4. WebGPUをONにする**

    .. image:: ../_static/tips/webgpu_ios_4.png
        :width: 320px
        :alt: WebGPU

**5. Safariが起動している場合、一旦終了する**

    .. image:: ../_static/tips/webgpu_ios_5.png
        :width: 320px
        :alt: Close Safari

    (ホームボタンをダブルクリック、Safariの画面を上にスワイプ)

これにより、SafariでWebGPUが利用できるようになります。

.. warning::
    WebGPUは実験的機能であり、ブラウザの動作を不安定にする可能性があります。WebGPUを使用したい場合以外は無効化しておくことが望ましいです。
