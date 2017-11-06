import chainer
import numpy as np

from test.util import generate_kernel_test_case, wrap_template
from webdnn.frontend.chainer.converter import ChainerConverter

@wrap_template
def template(ksize=2, stride=None, pad=0, shape=(2, 4, 6, 8), description=""):
    vx = chainer.Variable(np.random.rand(*shape).astype(np.float32))
    vy = chainer.functions.average_pooling_2d(vx, ksize=ksize, stride=stride, pad=pad)
