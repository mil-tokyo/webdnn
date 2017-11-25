import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x0_shape, x1_shape, description: str = ""):
    x0 = tf.placeholder(np.float32, x0_shape, "x0")
    x1 = tf.placeholder(np.float32, x1_shape, "x1")
    y = tf.concat([x0, x1], 3)

    vx0 = np.random.rand(*x0_shape).astype(np.float32)
    vx1 = np.random.rand(*x1_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x0: vx0, x1: vx1})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x0, x1], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] Concat {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx0,
            graph.inputs[1]: vx1
        },
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x0_shape=[2, 4, 6, 8], x1_shape=[2, 4, 6, 9])
