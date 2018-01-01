from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.variable import Variable


class LocalResponseNormalization(Operator):
    """LocalResponseNormalization(name, n, k, alpha, beta)

    Operator same as local response normalization layer in Caffe. Only cross channel mode is supported; normalization is done for channel
    axis.

    For more detail, see: http://caffe.berkeleyvision.org/tutorial/layers/lrn.html

    Args:
        name (str): Operator name.
        n (float): Parameter n.
        k (float): Parameter k.
        alpha (float): Parameter alpha.
        beta (float): Parameter beta.

    Signature
        .. code::

            y, = op(x)

        - **x** - Input variable.
        - **y** - Output variable. Its order and shape is same as :code:`x`.
    """

    def __init__(self, name: Optional[str], n: float, k: float, alpha: float, beta: float):
        super().__init__(name)
        self.parameters["n"] = n
        self.parameters["k"] = k
        self.parameters["alpha"] = alpha
        self.parameters["beta"] = beta
        self.attributes.add(Tensorwise(Axis.N))
        self.attributes.add(Tensorwise(Axis.H))
        self.attributes.add(Tensorwise(Axis.W))

    def __call__(self, x: Variable):
        y = Variable(x.shape, x.order)

        self.append_input("x", x)
        self.append_output("y", y)
        return y,
