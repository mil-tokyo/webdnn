import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape=[2, 3, 4, 5], ksize=[1, 3, 3, 1], strides=[1, 1, 1, 1], padding="VALID", description: str = ""):
    from tensorflow.python.ops import nn
    x = tf.placeholder(np.float32, x_shape, "x")
    y = nn.max_pool(x, ksize=ksize, strides=strides, padding=padding)

    vx = np.random.rand(*x_shape).astype(np.float32) - 0.5
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})
        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    assert list(vy.shape) == list(graph.outputs[0].shape), f"(vy.shape)={vy.shape}, (graph.outputs[0].shape)={graph.outputs[0].shape}"
    generate_kernel_test_case(
        description=f"[TensorFlow] MaxPool {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy}
    )


def test():
    template()


def test_padding_valid():
    template(padding="VALID")


def test_padding_same_even_size():
    # pad: ((1,1), (1,1))
    template(padding="SAME", x_shape=[2, 5, 5, 3], ksize=[1, 3, 3, 1], strides=[1, 1, 1, 1])


def test_padding_same_odd_size():
    # pad: ((1,0), (1,0))
    template(padding="SAME", x_shape=[2, 4, 4, 3], ksize=[1, 2, 2, 1], strides=[1, 1, 1, 1])


def test_large_stride():
    template(x_shape=[2, 5, 5, 5], strides=[1, 2, 2, 1])


def test_no_cover_all():
    template(ksize=[1, 2, 2, 1], x_shape=[1, 2, 2, 5], strides=[1, 2, 2, 1], padding="SAME")
