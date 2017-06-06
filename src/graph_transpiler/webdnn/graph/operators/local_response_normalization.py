from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.axiswise import Axiswise
from webdnn.graph.operators.attributes.inplace import Inplace
from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
from webdnn.graph.variable import Variable


# FIXME: Improve documentation
class LocalResponseNormalization(Operator):
    """Operator same as local response normalization layer in Caffe.
    Only cross channel mode is supported; normalization is done for channel axis.

    see: http://caffe.berkeleyvision.org/tutorial/layers/lrn.html
    
    Args:
        name (str): Operator name.
        n (float): Parameter n.
        k (float): Parameter k.
        alpha (float): Parameter alpha.
        beta (float): Parameter beta.

    """

    def __init__(self, name: Optional[str], n: float, k: float, alpha: float, beta: float):
        super().__init__(name)
        self.parameters["n"] = n
        self.parameters["k"] = k
        self.parameters["alpha"] = alpha
        self.parameters["beta"] = beta
        self.attributes = {PostAxiswise(self, Axis.C),
                           Axiswise(self, Axis.C)}

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~webdnn.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~webdnn.graph.variable.Variable`: Output
        """
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
