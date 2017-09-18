Enabling WebGPU on iOS 11
=========================

.. toctree::
    :hidden:

    日本語版(Japanese) <./enable_webgpu_ios_ja>

- :doc:`for macOS <./enable_webgpu_macos>`
- :doc:`日本語版(Japanese) <./enable_webgpu_ios_ja>`

Safari web browser on iOS 11 has WebGPU as an experimental feature. WebGPU accelerates WebDNN considerably.
For default, WebGPU is disabled. This page describes how to enable WebGPU.

**1. Open Settings and tap Safari**

    .. image:: ../_static/tips/webgpu_ios_1.png
        :width: 320px
        :alt: Safari

**2. Tap Advanced**

    .. image:: ../_static/tips/webgpu_ios_2.png
        :width: 320px
        :alt: Advanced

**3. Tap Experimental Features**

    .. image:: ../_static/tips/webgpu_ios_3.png
        :width: 320px
        :alt: Experimental Features

**4. Turn on WebGPU**

    .. image:: ../_static/tips/webgpu_ios_4.png
        :width: 320px
        :alt: WebGPU

**5. If Safari is already running, close it once**

    .. image:: ../_static/tips/webgpu_ios_5.png
        :width: 320px
        :alt: Close Safari

    (Double-click home button and swipe up preview of Safari)

Now WebGPU is enabled on Safari.

.. warning::
    WebGPU is an experimental feature and may make the browser unstable.
    It should be disabled unless you want to use WebGPU.

