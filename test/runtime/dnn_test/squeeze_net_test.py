import numpy as np

from test.runtime.frontend_test.keras_test.util import KerasConverter
from test.util import generate_kernel_test_case


def test():
    from example.squeeze_net.model_keras import SqueezeNet
    model = SqueezeNet()
    vx = np.random.rand(1, 223, 223, 3).astype(np.float32) - 0.5
    vy = model.predict(vx, batch_size=1)

    graph = KerasConverter(batch_size=1).convert(model)
    x = graph.inputs[0]
    y = graph.outputs[0]

    generate_kernel_test_case(
        description=f"[dnn] SqueezeNet in Keras",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx},
        expected={y: vy},
        EPS=1e-2,
    )
