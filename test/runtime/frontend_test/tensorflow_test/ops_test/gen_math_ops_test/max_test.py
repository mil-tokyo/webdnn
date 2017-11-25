import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template
from webdnn.graph.axis import Axis
from webdnn.graph.order import OrderNHWC


@wrap_template
def template(x_shape=[2, 3, 4, 5], x_order=OrderNHWC, axis=Axis.C, keep_dims=False, description: str = ""):
    x = tf.placeholder(np.float32, x_shape)
    y = tf.reduce_max(x, axis=x_order.axes_dict[axis], keep_dims=keep_dims)

    vx = np.random.rand(*x_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    assert list(vy.shape) == list(graph.outputs[0].shape)

    generate_kernel_test_case(
        description=f"[TensorFlow] Max {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={
            graph.inputs[0]: vx
        },
        expected={graph.outputs[0]: vy},
    )


def test():
    template()


def test_keep_dims():
    template(keep_dims=True)
