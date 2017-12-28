import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(N=2, H=5, W=5, Cin=7, Cout=9, KH=3, KW=3, strides=[1, 1, 1, 1], padding="VALID", data_format="NHWC", description: str = ""):
    x_shape = [N, H, W, Cin] if data_format == "NHWC" else [N, Cin, H, W]
    w_shape = [KH, KW, Cin, Cout]

    x = tf.placeholder(np.float32, x_shape)
    w = tf.placeholder(np.float32, w_shape)
    y = tf.nn.conv2d(x, w, strides=strides, padding=padding, data_format=data_format)

    vx = np.random.rand(*x_shape).astype(np.float32)
    vw = np.random.rand(*w_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx, w: vw})
        graph = TensorFlowConverter(sess, batch_size=2).convert([x, w], [y])

    assert list(vy.shape) == list(graph.outputs[0].shape), f"(vy.shape)={vy.shape}, (graph.outputs[0].shape)={graph.outputs[0].shape}"
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


def test_padding_valid():
    template(padding="VALID")


def test_padding_valid_extra_apron():
    # Extra apron should be ignored (should perform as cover_all=False)
    # (H_in + (PH_begin + PH_end) - KH) % SH = (6 + (0+0) - 3) % 2 = 1  => 1 extra pixel is exist.
    template(H=6, W=6, KH=3, KW=3, padding="VALID", strides=[1, 2, 2, 1])


def test_padding_same_even_padding_size():
    # pad: ((1,1), (1,1))
    template(padding="SAME", H=5, W=5, KH=3, KW=3, strides=[1, 1, 1, 1])


def test_padding_same_odd_padding_size():
    # pad: ((1,0), (1,0))
    template(padding="SAME", H=4, W=4, KH=2, KW=2, strides=[1, 1, 1, 1])


def test_padding_same_extra_apron():
    # Extra apron should be ignored (should perform as cover_all=False)
    # (H_in + (PH_begin + PH_end) - KH) % SH = (6 + (1+1) - 3) % 2 = 1  => 1 extra pixel is exist.
    template(H=6, W=6, KH=3, KW=3, padding="SAME", strides=[1, 2, 2, 1])


def test_projection():
    template(KH=1, KW=1)


def test_large_stride():
    template(strides=[1, 2, 2, 1])
