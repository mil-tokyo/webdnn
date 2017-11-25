import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(N=2, Hin=5, Hout=3, Win=5, Wout=3, Cin=7, Cout=9, KH=3, KW=3, strides=[1, 1, 1, 1], padding="VALID", data_format="NHWC",
             description: str = ""):
    from tensorflow.python.ops import nn
    x_shape = [N, Hin, Win, Cin] if data_format == "NHWC" else [N, Cin, Hin, Win]
    y_shape = [N, Hout, Wout, Cout] if data_format == "NHWC" else [N, Cout, Hout, Wout]
    w_shape = [KH, KW, Cin, Cout]
    w = tf.placeholder(np.float32, w_shape)
    gy = tf.placeholder(np.float32, y_shape)
    x = nn.conv2d_backprop_input(x_shape, w, gy, strides=strides, padding=padding, data_format=data_format)

    vw = np.random.rand(*w_shape).astype(np.float32)
    vgy = np.random.rand(*y_shape).astype(np.float32)

    with tf.Session() as sess:
        vx, = sess.run([x], {w: vw, gy: vgy})
        graph = TensorFlowConverter(sess, batch_size=2).convert([w, gy], [x])

    generate_kernel_test_case(
        description=f"[TensorFlow] Conv2DBackPropInput {description}",
        graph=graph,
        backend=["webgpu", "webassembly", "webgl"],
        inputs={
            graph.inputs[0]: vw,
            graph.inputs[1]: vgy
        },
        expected={graph.outputs[0]: vx}
    )


def test():
    template()


def test_pad_same():
    template(padding="SAME", Hout=5, Wout=5)


def test_projection():
    template(KH=1, KW=1, Hout=5, Wout=5)


def test_global_pooling():
    template(KH=5, KW=5, Hout=1, Wout=1)


def test_large_stride():
    template(strides=[1, 2, 2, 1], Hout=2, Wout=2)
