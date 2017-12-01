import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(axis, keep_dims, description: str = ""):
    x = tf.placeholder(np.float32, [2, 3, 4, 5])
    y = tf.reduce_min(x, axis=axis, keep_dims=keep_dims)

    vx = np.random.rand(2, 3, 4, 5).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    x = graph.inputs[0]
    y = graph.outputs[0]

    assert list(vy.shape) == list(y.shape), f"{vy.shape}, {y.shape}"
    generate_kernel_test_case(
        description=f"[TensorFlow] Min {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={x: vx},
        expected={y: vy},
    )


def test_axis_tuple():
    template(axis=(1, 3), keep_dims=True)


def test_axis_int():
    template(axis=1, keep_dims=True)


def test_axis_none():
    template(axis=None, keep_dims=True)


def test_no_keepdims():
    template(axis=(1, 3), keep_dims=False)
