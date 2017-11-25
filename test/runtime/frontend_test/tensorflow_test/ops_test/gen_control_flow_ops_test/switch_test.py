import numpy as np

from test.runtime.frontend_test.tensorflow_test.util import TensorFlowConverter, tf
from test.util import generate_kernel_test_case, wrap_template


@wrap_template
def template(x_shape=[2, 3, 4, 5], pred=True, description: str = ""):
    from tensorflow.python.ops import control_flow_ops

    x = tf.placeholder(np.float32, x_shape)
    y_f, y_t = control_flow_ops.switch(x, pred)
    y = y_t if pred else y_f

    vx = np.random.rand(*x_shape).astype(np.float32)
    with tf.Session() as sess:
        vy, = sess.run([y], {x: vx})
        graph = TensorFlowConverter(sess, batch_size=2).convert([x], [y])

    generate_kernel_test_case(
        description=f"[TensorFlow] Switch {description}",
        graph=graph,
        inputs={graph.inputs[0]: vx},
        expected={graph.outputs[0]: vy},
    )


def test_true():
    template(pred=True)


def test_false():
    template(pred=False)
