WebGPUをmacOS 10.13 High Sierraで有効にする方法
===============================================

- :doc:`iOSの場合 <./enable_webgpu_ios_ja>`
- :doc:`English <./enable_webgpu_macos>`

macOS 10.13 High Sierraに搭載のWebブラウザSafariには、実験的機能としてWebGPUが搭載されています。WebGPUにより、WebDNNの動作は大幅に高速化されます。
初期設定ではWebGPUは無効になっているため、このページでは、WebGPUを有効にする方法を説明します。

**1. Safariを起動し、「環境設定」を選択**

    .. image:: ../_static/tips/webgpu_macos_1_ja.png
        :width: 320px
        :alt: Open preferences

**2. 「メニューバーに"開発"メニューを表示」にチェックを入れる**

    .. image:: ../_static/tips/webgpu_macos_2_ja.png
        :width: 640px
        :alt: Develop menu

**3. メニューバーから"開発 > 実験的な機能 > WebGPU"にチェックを入れる**

    .. image:: ../_static/tips/webgpu_macos_3_ja.png
        :width: 480px
        :alt: Enable WebGPU

**4. Safariを再起動する**

これにより、SafariでWebGPUが利用できるようになります。

.. warning::
    WebGPUは実験的機能であり、ブラウザの動作を不安定にする可能性があります。WebGPUを使用したい場合以外は無効化しておくことが望ましいです。
