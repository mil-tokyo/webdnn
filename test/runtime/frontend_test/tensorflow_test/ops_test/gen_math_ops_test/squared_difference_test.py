import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape, y_shape, description: str = ""):
    x = tf.placeholder(np.float32, x_shape, "x")
    y = tf.placeholder(np.float32, y_shape, "y")
    z = tf.squared_difference(x, y)

    vx = np.random.rand(*x_shape).astype(np.float32)
    vy = np.random.rand(*y_shape).astype(np.float32)
    with tf.Session() as sess:
        vz, = sess.run([z], {x: vx, y: vy})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x, y], [z])

    generate_kernel_test_case(
        description=f"[TensorFlow] SquaredDifference {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx,
            graph.inputs[1]: vy
        },
        expected={graph.outputs[0]: vz},
    )


def test():
    template(x_shape=[2, 3, 4, 5], y_shape=[2, 3, 4, 5])


def test_broadcast1():
    template(x_shape=[2, 3, 4, 5], y_shape=[5])


def test_broadcast2():
    template(x_shape=[2, 3, 4, 5], y_shape=[1, 5])


def test_broadcast3():
    template(x_shape=[2, 3, 4, 5], y_shape=[1, 1, 1, 5])


def test_broadcast4():
    template(x_shape=[2, 1, 4, 1], y_shape=[1, 3, 1, 5])


def test_broadcast5():
    template(x_shape=[1, 1, 4, 1], y_shape=[1, 1, 1, 5])
