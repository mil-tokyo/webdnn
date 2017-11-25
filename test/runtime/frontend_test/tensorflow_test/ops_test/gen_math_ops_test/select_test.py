import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(cond_shape, x0_shape, x1_shape, description: str = ""):
    cond = tf.placeholder(np.bool, cond_shape)
    x0 = tf.placeholder(np.float32, x0_shape, "x0")
    x1 = tf.placeholder(np.float32, x1_shape, "x1")
    y = tf.where(cond, x0, x1)

    vcond = np.random.rand(*cond_shape) > 0.5
    vx0 = np.random.rand(*x0_shape).astype(np.float32)
    vx1 = np.random.rand(*x1_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {cond: vcond, x0: vx0, x1: vx1})

        graph = TensorFlowConverter(sess, batch_size=2).convert([cond, x0, x1], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] Select {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={
            graph.inputs[0]: vcond,
            graph.inputs[1]: vx0,
            graph.inputs[2]: vx1
        },
        expected={graph.outputs[0]: vy},
    )


def test():
    template(cond_shape=[2, 3, 4, 5], x0_shape=[2, 3, 4, 5], x1_shape=[2, 3, 4, 5])
