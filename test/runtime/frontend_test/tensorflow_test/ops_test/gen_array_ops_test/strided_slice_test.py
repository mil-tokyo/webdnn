import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case


def template(x: tf.Tensor, y, description: str = ""):
    vx = np.random.rand(*[dim.value for dim in x.shape.dims]).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})

        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    assert list(vy.shape) == list(graph.outputs[0].shape), f"vy_shape: {vy.shape}, y.shape: {graph.outputs[0].shape}"

    generate_kernel_test_case(
        description=f"[TensorFlow] StridedSlice {description}",
        graph=graph,
        backend=["webgpu", "webgl", "webassembly"],
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:1, 2:3, 3:5, 4:7]
    template(x, y)


def test_negative_index():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:1, 2:3, 1:-1, 2:-2]
    template(x, y)


def test_reversed():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[1:0:-1, 3:2:-1, 5:3:-1, 7:4:-1]
    template(x, y, "reversed")


def test_omit_start():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[:1, :3, :5, :7]
    template(x, y, "omit start")


def test_omit_start_reversed():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[:0:-1, :3:-1, :5:-1, :7:-1]
    template(x, y, "omit start reversed")


def test_omit_end():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:, 2:, 3:, 4:]
    template(x, y, "omit end")


def test_omit_end_reversed():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[1::-1, 2::-1, 3::-1, 4::-1]
    template(x, y, "omit end reversed")


def test_omit_both():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[:, :, :, :]
    template(x, y, "omit both")


def test_omit_both_reversed():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[::-1, ::-1, ::-1, ::-1]
    template(x, y, "omit both")


def test_new_axis():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:1, 2:3, None, 3:5, 4:7]
    template(x, y, "insert new axis")


def test_shrink():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:1, 2, 3:5, 4:7]
    template(x, y, "shrink axis")


def test_large_stride():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:1, ::2, ::2, 1::3]
    template(x, y, "shrink axis")


def test_explicit_ellipsis():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:2, ..., 1:5]
    template(x, y, "ellipsis")


def test_implicit_ellipsis():
    x = tf.placeholder(np.float32, [2, 4, 6, 8])
    y = x[0:2]
    template(x, y, "ellipsis")
