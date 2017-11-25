import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape, perm, description: str = ""):
    x = tf.placeholder(np.float32, x_shape)
    y = tf.transpose(x, perm=perm)

    vx = np.random.rand(*x_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] Transpose {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 4, 6, 8], perm=[0, 2, 3, 1])
