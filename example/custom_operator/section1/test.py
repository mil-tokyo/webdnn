import keras
import square

from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.frontend.keras.converter import KerasConverter

# ---------------------------------------------------------------------------------------------------
# Define Keras model

x = keras.layers.Input((10,))
y = square.SquareLayer()(x)
model = keras.models.Model([x], [y])

# ---------------------------------------------------------------------------------------------------
# Convert Keras model into WebDNN graph IR
graph = KerasConverter(batch_size=1).convert(model)

# ---------------------------------------------------------------------------------------------------
# Generate graph descriptors
WebGPUDescriptorGenerator.generate(graph).save("./output")
WebassemblyDescriptorGenerator.generate(graph).save("./output")
FallbackDescriptorGenerator.generate(graph).save("./output")
