operators
=========

Module :code:`webdnn.graph.operators` contains WebDNN Operator IR classes.
All classes inherit :class:`~webdnn.Operator` base class.

All operator class instances are callable. When it is called, input and output variables are registered with corresponding names.
In this document, the registered name of each operator is described in **Signature** section.

For almost of all users, it is not need to understand this section. If you want to implement your custom converter/generator handler,
this section may be helpful.

.. toctree::
    :maxdepth: 2

Abs
---
.. autoclass:: webdnn.graph.operators.abs.Abs
   :members:

AveragePooling2D
----------------
.. autoclass:: webdnn.graph.operators.average_pooling_2d.AveragePooling2D
   :members:

AxiswiseBias
------------
.. autoclass:: webdnn.graph.operators.axiswise_bias.AxiswiseBias
   :members:

AxiswiseScale
-------------
.. autoclass:: webdnn.graph.operators.axiswise_scale.AxiswiseScale
   :members:

ClippedRelu
-----------
.. autoclass:: webdnn.graph.operators.clipped_relu.ClippedRelu
   :members:

Concat
------
.. autoclass:: webdnn.graph.operators.concat.Concat
   :members:

Convolution2D
-------------
.. autoclass:: webdnn.graph.operators.convolution2d.Convolution2D
   :members:

Deconvolution2D
---------------
.. autoclass:: webdnn.graph.operators.deconvolution2d.Deconvolution2D
   :members:

Elementwise
-----------
.. autoclass:: webdnn.graph.operators.elementwise.Elementwise
   :members:

ElementwiseAdd
--------------
.. autoclass:: webdnn.graph.operators.elementwise_add.ElementwiseAdd
   :members:

ElementwiseDiv
--------------
.. autoclass:: webdnn.graph.operators.elementwise_div.ElementwiseDiv
   :members:

ElementwiseMul
--------------
.. autoclass:: webdnn.graph.operators.elementwise_mul.ElementwiseMul
   :members:

ElementwisePow
--------------
.. autoclass:: webdnn.graph.operators.elementwise_pow.ElementwisePow
   :members:

Elu
---
.. autoclass:: webdnn.graph.operators.elu.Elu
   :members:

Embedding
---------
.. autoclass:: webdnn.graph.operators.embedding.Embedding
   :members:

HardSigmoid
-----------
.. autoclass:: webdnn.graph.operators.hard_sigmoid.HardSigmoid
   :members:

LeakyRelu
---------
.. autoclass:: webdnn.graph.operators.leaky_relu.LeakyRelu
   :members:

Linear
------
.. autoclass:: webdnn.graph.operators.linear.Linear
   :members:

LocalResponseNormalization
--------------------------
.. autoclass:: webdnn.graph.operators.local_response_normalization.LocalResponseNormalization
   :members:

MaxPooling2D
------------
.. autoclass:: webdnn.graph.operators.max_pooling_2d.MaxPooling2D
   :members:

Pooling2D
---------
.. autoclass:: webdnn.graph.operators.pooling_2d.Pooling2D
   :members:

ReinterpretAxis
---------------
.. autoclass:: webdnn.graph.operators.reinterpret_axis.ReinterpretAxis
   :members:

Relu
----
.. autoclass:: webdnn.graph.operators.relu.Relu
   :members:

Reshape
-------
.. autoclass:: webdnn.graph.operators.reshape.Reshape
   :members:

ScalarAdd
---------
.. autoclass:: webdnn.graph.operators.scalar_add.ScalarAdd
   :members:

ScalarAffine
------------
.. autoclass:: webdnn.graph.operators.scalar_affine.ScalarAffine
   :members:

ScalarMul
---------
.. autoclass:: webdnn.graph.operators.scalar_mul.ScalarMul
   :members:

ScalarPow
---------
.. autoclass:: webdnn.graph.operators.scalar_pow.ScalarPow
   :members:

Sigmoid
-------
.. autoclass:: webdnn.graph.operators.sigmoid.Sigmoid
   :members:

Softmax
-------
.. autoclass:: webdnn.graph.operators.softmax.Softmax
   :members:

Softplus
--------
.. autoclass:: webdnn.graph.operators.softplus.Softplus
   :members:

Softsign
--------
.. autoclass:: webdnn.graph.operators.softsign.Softsign
   :members:

Tanh
----
.. autoclass:: webdnn.graph.operators.tanh.Tanh
   :members:

ThresholdRelu
-------------
.. autoclass:: webdnn.graph.operators.threshold_relu.ThresholdRelu
   :members:

ZeroPadding1D
-------------
.. autoclass:: webdnn.graph.operators.zero_padding_1d.ZeroPadding1D
   :members:

ZeroPadding2D
-------------
.. autoclass:: webdnn.graph.operators.zero_padding_2d.ZeroPadding2D
   :members:
