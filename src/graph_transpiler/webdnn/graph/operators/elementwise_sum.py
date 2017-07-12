import warnings

from webdnn.graph.operators.elementwise_add import ElementwiseAdd


class ElementwiseSum(ElementwiseAdd):
    def __init__(self, *args, **kwargs):
        # FIXME: In v1.3.0, ElementwiseSum will be removed.
        warnings.warn("ElementwiseSum will be removed in the future version. Use ElementwiseAdd.", DeprecationWarning, stacklevel=2)
        super(ElementwiseSum, self).__init__(*args, **kwargs)
