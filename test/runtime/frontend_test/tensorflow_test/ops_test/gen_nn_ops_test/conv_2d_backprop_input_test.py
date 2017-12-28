import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(N=2, Hin=5, Hout=3, Win=5, Wout=3, Cin=1, Cout=1, KH=3, KW=3, strides=[1, 1, 1, 1], padding="VALID", data_format="NHWC",
             description: str = ""):
    x_shape = [N, Hin, Win, Cin] if data_format == "NHWC" else [N, Cin, Hin, Win]
    y_shape = [N, Hout, Wout, Cout] if data_format == "NHWC" else [N, Cout, Hout, Wout]
    w_shape = [KH, KW, Cin, Cout]
    w = tf.placeholder(np.float32, w_shape)
    gy = tf.placeholder(np.float32, y_shape)
    x = tf.nn.conv2d_backprop_input(x_shape, w, gy, strides=strides, padding=padding, data_format=data_format)

    vw = np.random.rand(*w_shape).astype(np.float32)
    vgy = np.random.rand(*y_shape).astype(np.float32)

    with tf.Session() as sess:
        vx, = sess.run([x], {w: vw, gy: vgy})
        graph = TensorFlowConverter(sess, batch_size=2).convert([w, gy], [x])

    assert list(vx.shape) == list(graph.outputs[0].shape), f"(vx.shape)={vx.shape}, (graph.outputs[0].shape)={graph.outputs[0].shape}"
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


def test_padding_valid():
    template(padding="VALID")


def test_padding_valid_extra_apron():
    # Case that convolution input has extra apron which is ignored.
    # (Computed H_in) = (H_out-1)*SH + KH - (PH_begin+PH_end) = (2-1)*2 + 3 - 0 = 5 => 6-5=1 pixel is apron
    template(Hin=6, Win=6, Hout=2, Wout=2, KH=3, KW=3, padding="VALID", strides=[1, 2, 2, 1])


def test_padding_same_even_padding_size():
    # pad: ((1,1), (1,1))
    template(padding="SAME", Hin=5, Win=5, Hout=5, Wout=5, KH=3, KW=3, strides=[1, 1, 1, 1])


def test_padding_same_odd_padding_size():
    # pad: ((1,0), (1,0))
    template(padding="SAME", Hin=4, Win=4, Hout=4, Wout=4, KH=2, KW=2, strides=[1, 1, 1, 1])


def test_padding_same_extra_apron():
    # (Computed H_in) = (H_out-1)*SH + KH - (PH_begin+PH_end) = (2-1)*3 + 3 - 2 = 4 => 6-4=2 pixel is apron
    # padding (2px) must be canceled with apron pixels (2px)
    template(Hin=6, Win=6, Hout=2, Wout=2, KH=3, KW=3, padding="SAME", strides=[1, 3, 3, 1])


def test_large_stride():
    template(strides=[1, 2, 2, 1], Hout=2, Wout=2)
