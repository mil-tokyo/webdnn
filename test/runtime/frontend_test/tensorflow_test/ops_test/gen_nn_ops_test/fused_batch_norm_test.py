import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape=[2, 3, 4, 5], data_format="NHWC", description: str = ""):
    from tensorflow.python.ops import nn
    x = tf.placeholder(np.float32, x_shape)
    scale = tf.placeholder(np.float32, x_shape[-1] if data_format == "NHWC" else x_shape[1])
    bias = tf.placeholder(np.float32, x_shape[-1] if data_format == "NHWC" else x_shape[1])
    mean = tf.placeholder(np.float32, x_shape[-1] if data_format == "NHWC" else x_shape[1])
    variance = tf.placeholder(np.float32, x_shape[-1] if data_format == "NHWC" else x_shape[1])
    y, _, _ = nn.fused_batch_norm(x, scale, bias, mean, variance, data_format=data_format, is_training=False)

    vx = np.random.rand(*x_shape).astype(np.float32)
    vs = np.random.rand(*[x_shape[-1] if data_format == "NHWC" else x_shape[1]]).astype(np.float32)
    vb = np.random.rand(*[x_shape[-1] if data_format == "NHWC" else x_shape[1]]).astype(np.float32)
    vm = np.random.rand(*[x_shape[-1] if data_format == "NHWC" else x_shape[1]]).astype(np.float32)
    vv = np.random.rand(*[x_shape[-1] if data_format == "NHWC" else x_shape[1]]).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx, scale: vs, bias: vb, mean: vm, variance: vv})
        graph = TensorFlowConverter(sess, batch_size=2).convert([x, scale, bias, mean, variance], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] FusedBatchNorm {description}",
        graph=graph,
        inputs={
            graph.inputs[0]: vx,
            graph.inputs[1]: vs,
            graph.inputs[2]: vb,
            graph.inputs[3]: vm,
            graph.inputs[4]: vv
        },
        expected={graph.outputs[0]: vy},
    )


def test_NHWC():
    template(data_format="NHWC")


# FIXME: TensorFlow supports only NHWC mode in CPU
# def test_NCHW():
#     template(data_format="NCHW")
