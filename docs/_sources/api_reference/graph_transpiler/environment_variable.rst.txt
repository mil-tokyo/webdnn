Environment Variables
=====================

You can control graph transpiler behavior by follow environment variables.

.. code-block:: bash

    # ex)
    $ DEBUG=1 OPTIMIZE=0 ./bin/convert_keras.py my_keras_model.h5 --backend webgpu --out ./output


.. envvar:: DEBUG

    If :code:`1`, debug log is printed out. Default is :code:`0`.

.. envvar:: OPTIMIZE

    If :code:`1`, all optimization rule is applied. Otherwise, no optimization rule is applied. Default is :code:`1`.

