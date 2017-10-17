import sys
import os
from typing import Optional, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
'''
Custom Keras layers used on the pastiche model.
'''

import tensorflow as tf
import keras
from keras import initializers
from keras.layers import ZeroPadding2D, Layer, InputSpec


# Extending the ZeroPadding2D layer to do reflection padding instead.
class ReflectionPadding2D(ZeroPadding2D):
    def call(self, x, mask=None):
        pattern = [[0, 0],
                   self.padding[0],
                   self.padding[1],
                   [0, 0]]
        return tf.pad(x, pattern, mode='REFLECT')


class InstanceNormalization(Layer):
    def __init__(self, epsilon=1e-5, weights=None,
                 beta_init='zero', gamma_init='one', **kwargs):
        self.beta_init = initializers.get(beta_init)
        self.gamma_init = initializers.get(gamma_init)
        self.epsilon = epsilon
        super(InstanceNormalization, self).__init__(**kwargs)

    def build(self, input_shape):
        # This currently only works for 4D inputs: assuming (B, H, W, C)
        self.input_spec = [InputSpec(shape=input_shape)]
        shape = (1, 1, 1, input_shape[-1])


        self.gamma = self.add_weight(name='{}_gamma'.format(self.name),
                                      shape=shape,
                                      initializer='uniform',
                                      trainable=True)
        self.beta = self.add_weight(name='{}_beta'.format(self.name),
                                      shape=shape,
                                      initializer='uniform',
                                      trainable=True)
        self.trainable_weights = [self.gamma, self.beta]

        self.built = True

    def call(self, x, mask=None):
        # Do not regularize batch axis
        reduction_axes = [1, 2]

        mean, var = tf.nn.moments(x, reduction_axes,
                                  shift=None, name=None, keep_dims=True)
        x_normed = tf.nn.batch_normalization(x, mean, var, self.beta, self.gamma, self.epsilon)
        return x_normed

    def get_config(self):
        config = {"epsilon": self.epsilon}
        base_config = super(InstanceNormalization, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ConditionalInstanceNormalization(InstanceNormalization):
    def __init__(self, targets, nb_classes, **kwargs):
        self.targets = targets
        self.nb_classes = nb_classes
        super(ConditionalInstanceNormalization, self).__init__(**kwargs)

    def build(self, input_shape):
        # This currently only works for 4D inputs: assuming (B, H, W, C)
        self.input_spec = [InputSpec(shape=input_shape)]
        shape = (self.nb_classes, 1, 1, input_shape[-1])

        self.gamma = self.gamma_init(shape, name='{}_gamma'.format(self.name))
        self.beta = self.beta_init(shape, name='{}_beta'.format(self.name))
        self.trainable_weights = [self.gamma, self.beta]

        self.built = True

    def call(self, x, mask=None):
        # Do not regularize batch axis
        reduction_axes = [1, 2]

        mean, var = tf.nn.moments(x, reduction_axes,
                                  shift=None, name=None, keep_dims=True)

        # Get the appropriate lines of gamma and beta
        beta = tf.gather(self.beta, self.targets)
        gamma = tf.gather(self.gamma, self.targets)
        x_normed = tf.nn.batch_normalization(x, mean, var, beta, gamma, self.epsilon)

        return x_normed


from webdnn.frontend.keras.converter import KerasConverter
from webdnn.frontend.keras.layers.convolutional import _convert_zero_padding2d
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderC, OrderNHWC
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable
from webdnn.graph.operators.scalar_mul import ScalarMul


@KerasConverter.register_handler("ReflectionPadding2D")
def reflection_padding_2d_converter_handler(converter: KerasConverter, keras_layer: ReflectionPadding2D):
    # TODO: correct implementation
    _convert_zero_padding2d(converter, keras_layer)


class Moment(Operator):
    def __init__(self, name: Optional[str], eps: float):
        super().__init__(name)
        self.parameters["eps"] = eps

    def __call__(self, x: Variable):
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        C = x_shape_dict[Axis.C]

        y_mean = Variable([N, 1, 1, C], OrderNHWC)
        y_mean.change_order(x.order)  # output same order as input to preserve following reshape semantics

        y_inv_std = Variable([N, 1, 1, C], OrderNHWC)
        y_inv_std.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_input("x", x)
        self.append_output("y_mean", y_mean)
        self.append_output("y_inv_std", y_inv_std)
        return y_mean, y_inv_std


@KerasConverter.register_handler("InstanceNormalization")
def instance_normalization_converter_handler(converter: KerasConverter, keras_layer: InstanceNormalization):
    keras_x = converter.get_input_tensor(keras_layer)[0]
    webdnn_x = converter.get_variable(keras_x)

    webdnn_beta = converter.convert_to_constant_variable(keras_layer.beta, OrderNHWC)
    webdnn_gamma = converter.convert_to_constant_variable(keras_layer.gamma, OrderNHWC)
    op_moment = Moment(None, keras_layer.epsilon)
    webdnn_mean, webdnn_inv_std = op_moment(webdnn_x)
    webdnn_y = (webdnn_x - webdnn_mean) * webdnn_inv_std * webdnn_gamma + webdnn_beta
    keras_y = converter.get_output_tensor(keras_layer)[0]

    converter.set_variable(keras_y, webdnn_y)


@KerasConverter.register_handler("Merge")
def merge_converter_handler(converter: KerasConverter, keras_layer):
    assert keras_layer.mode == "sum"
    keras_x0 = converter.get_input_tensor(keras_layer)[0]
    keras_x1 = converter.get_input_tensor(keras_layer)[1]
    webdnn_x0 = converter.get_variable(keras_x0)
    webdnn_x1 = converter.get_variable(keras_x1)

    webdnn_y = webdnn_x0 + webdnn_x1
    keras_y = converter.get_output_tensor(keras_layer)[0]

    converter.set_variable(keras_y, webdnn_y)

class UpSampling2D(Operator):
    def __init__(self, name: Optional[str], size: Tuple[int, int]):
        super().__init__(name)
        self.parameters["size"] = size

    def __call__(self, x: Variable):
        x_shape_dict = x.shape_dict
        N = x_shape_dict[Axis.N]
        H2 = x_shape_dict[Axis.H] * self.parameters["size"][0]
        W2 = x_shape_dict[Axis.W] * self.parameters["size"][1]
        C2 = x_shape_dict[Axis.C]

        y = Variable([N, H2, W2, C2], OrderNHWC)
        y.change_order(x.order)  # output same order as input to preserve following reshape semantics

        self.append_input("x", x)
        self.append_output("y", y)
        return y,

@KerasConverter.register_handler("UpSampling2D")
def upsampling_2d_converter_handler(converter: KerasConverter, keras_layer):
    keras_x = converter.get_input_tensor(keras_layer)[0]
    webdnn_x = converter.get_variable(keras_x)

    op = UpSampling2D(None, size=keras_layer.size)
    webdnn_y, = op(webdnn_x)
    keras_y = converter.get_output_tensor(keras_layer)[0]

    converter.set_variable(keras_y, webdnn_y)

@KerasConverter.register_handler("Lambda")
def lambda_converter_handler(converter: KerasConverter, keras_layer):
    # Assuming o = Lambda(lambda x: 150*x, name='scaling')(o)
    keras_x = converter.get_input_tensor(keras_layer)[0]
    webdnn_x = converter.get_variable(keras_x)

    webdnn_y = webdnn_x * 150.0
    keras_y = converter.get_output_tensor(keras_layer)[0]

    converter.set_variable(keras_y, webdnn_y)
