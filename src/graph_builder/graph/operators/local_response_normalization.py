from typing import Optional

from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.post_axiswise import PostAxiswise
from graph_builder.graph.operators.attributes.post_elementwise import PostElementwise
from graph_builder.graph.variable import Variable


# FIXME: Improve documentation
class LocalResponseNormalization(Operator):
    """Operator same as local response normalization layer in Caffe. 

    see: http://caffe.berkeleyvision.org/tutorial/layers/lrn.html
    
    Args:
        name (str): Operator name.
        n (float): Parameter n.
        k (float): Parameter k.
        alpha (float): Parameter alpha.
        beta (float): Parameter beta.

    """
    attributes = {PostElementwise,
                  PostAxiswise}

    def __init__(self, name: Optional[str], n: float, k: float, alpha: float, beta: float):
        super().__init__(name)
        self.parameters["n"] = n
        self.parameters["k"] = k
        self.parameters["alpha"] = alpha
        self.parameters["beta"] = beta

    def __call__(self, x: Variable):
        """
        Args:
            x (:class:`~graph_builder.graph.variable.Variable`): Input

        Returns:
            tuple of :class:`~graph_builder.graph.variable.Variable`: Output
        """
        y = Variable(x.shape, x.order)
        self.append_input("x", x)
        self.append_output("y", y)
        return y,
