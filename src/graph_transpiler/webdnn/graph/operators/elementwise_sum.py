import warnings

from webdnn.graph.operators.elementwise_add import ElementwiseAdd


class ElementwiseSum(ElementwiseAdd):
    """
    .. deprecated:: v1.2
       Use :class:`~webdnn.graph.operators.elementwise_add.ElementwiseAdd` instead.
    """

    def __init__(self, *args, **kwargs):
        # FIXME: Deprecated
        warnings.warn("ElementwiseSum will be removed in the future version. Use ElementwiseAdd.", DeprecationWarning, stacklevel=2)
        super(ElementwiseSum, self).__init__(*args, **kwargs)
