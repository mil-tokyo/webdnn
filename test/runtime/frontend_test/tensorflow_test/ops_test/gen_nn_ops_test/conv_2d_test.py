import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(N=2, H=5, W=5, Cin=7, Cout=9, KH=3, KW=3, strides=[1, 1, 1, 1], padding="VALID", data_format="NHWC", description: str = ""):
    from tensorflow.python.ops import nn
    x_shape = [N, H, W, Cin] if data_format == "NHWC" else [N, Cin, H, W]
    w_shape = [KH, KW, Cin, Cout]

    x = tf.placeholder(np.float32, x_shape)
    w = tf.placeholder(np.float32, w_shape)
    y = nn.conv2d(x, w, strides=strides, padding=padding, data_format=data_format)

    vx = np.random.rand(*x_shape).astype(np.float32)
    vw = np.random.rand(*w_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx, w: vw})
        graph = TensorFlowConverter(sess, batch_size=2).convert([x, w], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] Conv2D {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx,
            graph.inputs[1]: vw
        },
        expected={graph.outputs[0]: vy}
    )


def test():
    template()


def test_pad_same():
    template(padding="SAME")


def test_projection():
    template(KH=1, KW=1)


def test_global_pooling():
    template(KH=5, KW=5)


def test_large_stride():
    template(strides=[1, 2, 2, 1])
