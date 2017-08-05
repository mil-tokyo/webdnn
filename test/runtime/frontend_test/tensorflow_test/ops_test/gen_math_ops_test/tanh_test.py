import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape, description: str = ""):
    x = tf.placeholder(np.float32, x_shape, "x")
    y = tf.tanh(x)

    vx = np.random.rand(*x_shape) - 0.5
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] Sigmoid {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx, },
        expected={graph.outputs[0]: vy},
    )


def test():
    template(x_shape=[2, 3, 4, 5])
