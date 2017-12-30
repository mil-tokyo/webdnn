import warnings
from typing import Optional

from webdnn.graph.axis import Axis
from webdnn.graph.operators.elementwise_mul import ElementwiseMul


class AxiswiseScale(ElementwiseMul):
    """AxiswiseScale(name, axis)

    Multiply a scale value along to specified axis.

    Args:
        name (str): Operator name.
        axis (:obj:`~webdnn.Axis`): target axis

    Signature
        .. code::

            y, = op(x, s)

        - **x** - Data variable. It must has `axis` axis, and whose size must be same as :code:`s`.
        - **s** - Scale variable. It must be 1D variable and that size must be same as :code:`x.shape_dict[axis]`
        - **y** - Output variable. Its order and shape is same as :code:`x`.

    .. deprecated:: v1.2
       Use :class:`~webdnn.graph.operators.elementwise_mul.ElementwiseMul` instead.
    """

    def __init__(self, name: Optional[str], axis: Axis):
        super().__init__(name)
        self.parameters["axis"] = axis

        # FIXME: Deprecated
        warnings.warn("AxiswiseScale will be removed in the future version. Use ElementwiseMul.", DeprecationWarning, stacklevel=2)

    @property
    def axis(self) -> Axis:
        return self.parameters["axis"]
