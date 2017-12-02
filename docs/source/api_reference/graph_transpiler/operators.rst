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

Acos
----
.. autoclass:: webdnn.graph.operators.acos.Acos
   :members:

Acosh
-----
.. autoclass:: webdnn.graph.operators.acosh.Acosh
   :members:

Asin
----
.. autoclass:: webdnn.graph.operators.asin.Asin
   :members:

Asinh
-----
.. autoclass:: webdnn.graph.operators.asinh.Asinh
   :members:

Atan
----
.. autoclass:: webdnn.graph.operators.atan.Atan
   :members:

Atanh
-----
.. autoclass:: webdnn.graph.operators.atanh.Atanh
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

Broadcast
---------
.. autoclass:: webdnn.graph.operators.broadcast.Broadcast
   :members:

ClippedRelu
-----------
.. autoclass:: webdnn.graph.operators.clipped_relu.ClippedRelu
   :members:

Col2Im
------
.. autoclass:: webdnn.graph.operators.col2im.Col2Im
   :members:

Concat
------
.. autoclass:: webdnn.graph.operators.concat.Concat
   :members:

Convolution2D
-------------
.. autoclass:: webdnn.graph.operators.convolution2d.Convolution2D
   :members:

Cos
---
.. autoclass:: webdnn.graph.operators.cos.Cos
   :members:

Cosh
----
.. autoclass:: webdnn.graph.operators.cosh.Cosh
   :members:

Deconvolution2D
---------------
.. autoclass:: webdnn.graph.operators.deconvolution2d.Deconvolution2D
   :members:

Depth2Space
-----------
.. autoclass:: webdnn.graph.operators.depth2space.Depth2Space
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

ElementwiseSum
--------------
.. autoclass:: webdnn.graph.operators.elementwise_sum.ElementwiseSum
   :members:

Elu
---
.. autoclass:: webdnn.graph.operators.elu.Elu
   :members:

Embedding
---------
.. autoclass:: webdnn.graph.operators.embedding.Embedding
   :members:

Exp
---
.. autoclass:: webdnn.graph.operators.exp.Exp
   :members:

Greater
-------
.. autoclass:: webdnn.graph.operators.greater.Greater
   :members:

GreaterEqual
------------
.. autoclass:: webdnn.graph.operators.greater_equal.GreaterEqual
   :members:

HardSigmoid
-----------
.. autoclass:: webdnn.graph.operators.hard_sigmoid.HardSigmoid
   :members:

Im2Col
------
.. autoclass:: webdnn.graph.operators.im2col.Im2Col
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

Log
---
.. autoclass:: webdnn.graph.operators.log.Log
   :members:

LSTM
----
.. autoclass:: webdnn.graph.operators.lstm.LSTM
   :members:

Max
---
.. autoclass:: webdnn.graph.operators.max.Max
   :members:

MaxPooling2D
------------
.. autoclass:: webdnn.graph.operators.max_pooling_2d.MaxPooling2D
   :members:

Pooling2D
---------
.. autoclass:: webdnn.graph.operators.pooling_2d.Pooling2D
   :members:

Prod
----
.. autoclass:: webdnn.graph.operators.prod.Prod
   :members:

Reduce
------
.. autoclass:: webdnn.graph.operators.reduce.Reduce
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

Rsqrt
-----------
.. autoclass:: webdnn.graph.operators.rsqrt.Rsqrt
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

Select
------
.. autoclass:: webdnn.graph.operators.select.Select
   :members:

Sigmoid
-------
.. autoclass:: webdnn.graph.operators.sigmoid.Sigmoid
   :members:

Sin
---
.. autoclass:: webdnn.graph.operators.sin.Sin
   :members:

Sinh
----
.. autoclass:: webdnn.graph.operators.sinh.Sinh
   :members:

Slice
-----
.. autoclass:: webdnn.graph.operators.slice.Slice
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

Space2Depth
-----------
.. autoclass:: webdnn.graph.operators.space2depth.Space2Depth
   :members:

Tan
---
.. autoclass:: webdnn.graph.operators.tan.Tan
   :members:

Tanh
----
.. autoclass:: webdnn.graph.operators.tanh.Tanh
   :members:

Tensordot
---------
.. autoclass:: webdnn.graph.operators.tensordot.Tensordot
   :members:

ThresholdRelu
-------------
.. autoclass:: webdnn.graph.operators.threshold_relu.ThresholdRelu
   :members:

Tile
----
.. autoclass:: webdnn.graph.operators.tile.Tile
   :members:

Transpose
---------
.. autoclass:: webdnn.graph.operators.transpose.Transpose
   :members:

Unpooling2D
-----------
.. autoclass:: webdnn.graph.operators.unpooling_2d.Unpooling2D
   :members:

ZeroPadding1D
-------------
.. autoclass:: webdnn.graph.operators.zero_padding_1d.ZeroPadding1D
   :members:

ZeroPadding2D
-------------
.. autoclass:: webdnn.graph.operators.zero_padding_2d.ZeroPadding2D
   :members:
