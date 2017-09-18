Enabling WebGPU on macOS 10.13 High Sierra
==========================================

.. toctree::
    :hidden:

    日本語版(Japanese) <./enable_webgpu_macos_ja>

- :doc:`for iOS <./enable_webgpu_ios>`
- :doc:`日本語版(Japanese) <./enable_webgpu_macos_ja>`

Safari web browser on macOS 10.13 High Sierra has WebGPU as an experimental feature. WebGPU accelerates WebDNN considerably.
For default, WebGPU is disabled. This page describes how to enable WebGPU.

**1. Launch Safari and open "Preferences"**

    .. image:: ../_static/tips/webgpu_macos_1.png
        :width: 320px
        :alt: Open preferences

**2. Select "Show Develop menu in menu bar"**

    .. image:: ../_static/tips/webgpu_macos_2.png
        :width: 640px
        :alt: Develop menu

**3. Select "Develop > Experimental Features > WebGPU" in menu bar.**

    .. image:: ../_static/tips/webgpu_macos_3.png
        :width: 480px
        :alt: Enable WebGPU

**4. Restart Safari**

Now WebGPU is enabled on Safari.

.. warning::
    WebGPU is an experimental feature and may make the browser unstable.
    It should be disabled unless you want to use WebGPU.
