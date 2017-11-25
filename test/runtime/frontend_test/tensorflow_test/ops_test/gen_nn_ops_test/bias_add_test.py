import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape=[2, 3, 4, 5], data_format="NHWC", description: str = ""):
    from tensorflow.python.ops import nn
    x = tf.placeholder(np.float32, x_shape)
    b = tf.placeholder(np.float32, x_shape[-1] if data_format == "NHWC" else x_shape[1])
    y = nn.bias_add(x, b, data_format)

    vx = np.random.rand(*x_shape).astype(np.float32)
    vb = np.random.rand(*[x_shape[-1] if data_format == "NHWC" else x_shape[1]]).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx, b: vb})
        graph = TensorFlowConverter(sess, batch_size=2).convert([x, b], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] BiasAdd {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx,
            graph.inputs[1]: vb
        },
        expected={graph.outputs[0]: vy},
    )


def test_NHWC():
    template(data_format="NHWC")


def test_NCHW():
    template(data_format="NCHW")
