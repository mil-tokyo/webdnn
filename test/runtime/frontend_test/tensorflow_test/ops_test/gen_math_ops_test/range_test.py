import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(start, limit, delta, x1_shape, description: str = ""):
    x0 = tf.range(start, limit, delta, dtype=np.float32)
    x1 = tf.placeholder(np.float32, x1_shape)
    y = x0 + x1

    vx1 = np.random.rand(*x1_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x1: vx1})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x1], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] Range {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx1},
        expected={graph.outputs[0]: vy},
    )


def test():
    template(start=2, limit=10, delta=1, x1_shape=(8,))
