import keras
import keras.backend as K
import numpy as np

from webdnn.frontend.keras.converter import KerasConverter
from webdnn.graph.order import Order
from webdnn.graph.variables.constant_variable import ConstantVariable


@KerasConverter.register_handler("BatchNormalization")
def _convert_batch_normalization(converter: KerasConverter, k_op: "keras.layers.BatchNormalization"):
    x = converter.get_variable(converter.get_input_tensor(k_op)[0])

    axis = x.order.axes[k_op.axis]

    variance_data, mean_data = K.batch_get_value([k_op.moving_variance, k_op.moving_mean])

    if k_op.scale:
        gamma_data, = K.batch_get_value([k_op.gamma])
    else:
        gamma_data = np.ones_like(variance_data)

    if k_op.center:
        beta_data, = K.batch_get_value([k_op.beta])
    else:
        beta_data = np.zeros_like(mean_data)

    gamma_div_std_data = gamma_data / np.sqrt(variance_data + k_op.epsilon)
    beta_scaled_data = beta_data - mean_data * gamma_div_std_data

    gamma_div_std = ConstantVariable(gamma_div_std_data, Order([axis]))
    beta_scaled = ConstantVariable(beta_scaled_data, Order([axis]))

    y = x * gamma_div_std + beta_scaled
    converter.set_variable(converter.get_output_tensor(k_op)[0], y)
