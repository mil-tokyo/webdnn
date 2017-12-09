import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape, paddings, mode, description: str = ""):
    x = tf.placeholder(np.float32, x_shape)
    y = tf.pad(x, paddings, mode=mode)

    vx = np.random.rand(*x_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    assert list(vy.shape) == list(y.shape)
    generate_kernel_test_case(
        description=f"[TensorFlow] MirrorPad {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test_reflect():
    template(x_shape=[2, 4, 6, 8], paddings=[[0, 1], [2, 3], [4, 5], [6, 7]], mode="REFLECT")


def test_symmetric():
    template(x_shape=[2, 4, 6, 8], paddings=[[0, 1], [2, 3], [4, 5], [6, 7]], mode="SYMMETRIC")


def test_no_pad():
    template(x_shape=[2, 4, 6, 8], paddings=[[0, 0], [0, 0], [0, 0], [0, 0]], mode="REFLECT")
