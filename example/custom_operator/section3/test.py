import bias
import keras
import numpy as np

from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.frontend.keras.converter import KerasConverter

# ---------------------------------------------------------------------------------------------------
# Define Keras model

x = keras.layers.Input((10,))
layer = bias.BiasLayer()
y = layer(x)
model = keras.models.Model([x], [y])

# For test, initialize bias by 100.
keras.backend.set_value(layer.bias, np.ones(layer.bias.shape) * 100)

# ---------------------------------------------------------------------------------------------------
# Convert Keras model into WebDNN graph IR
graph = KerasConverter(batch_size=1).convert(model)

# ---------------------------------------------------------------------------------------------------
# Generate graph descriptor
WebGPUDescriptorGenerator.generate(graph).save("./output")
WebassemblyDescriptorGenerator.generate(graph).save("./output")
FallbackDescriptorGenerator.generate(graph).save("./output")
