from webdnn.graph.attribute import Attribute
from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator


class Tensorwise(Attribute):
    """Tensorwise(axis)

    Tensorwise `Tensorwise[axis]` means that attached operator satisfied follow conditions.

    1. All input and output variables have `axis`.
    2. Size of the axis is same in all input and output variables (If broadcasting is performed, the size after broadcasting is same).
    3. This operation is tensorwise operation of `axis`.

    ex) Considering a binary operator `C = op(A, B)`,

                 A               B               C

               Axis1           Axis1           Axis1
              +--+--+         +--+--+         +--+--+
              |A1:A2|   Axis3 |B1:B2|   Axis4 |C1:C2|
        Axis2 |  :  |         +--+--+         |  :  |
              |  :  |                         +--+--+
              +--+--+

        1. All variables has `Axis1`.
        2. The size of `Axis1` is same in all variables.
        3. This operation is independent from axis1's position (To calculate C1, only A1 and B1 is needed, A2 and B2 is not required).

        Therefore, this operator has `Tensorwise[Axis1]` attribute.

    ex) Some use case:

    - `Elementwise` operation has `Tensorwise` attribute for all axes.
    - `Pooling2D` operation has `Tensorwise[Axis.N]` and `Tensorwise[Axis.C]`, NOT has `Tensorwise[Axis.H]` and `Tensorwise[Axis.W]`.
    - `Sgemm` operation doesn't has any Tensorwise attribute.

    Attributes:
        axis (:class:`~webdnn.graph.axis.Axis`): the axis
    """

    def __init__(self, axis: Axis):
        self.axis = axis

    def __str__(self):
        return f"Tensorwise[{self.axis.name}]"

    @staticmethod
    def check_splittable(op: Operator, axis: Axis):
        """Check whether op can be split in specified axis"""
        return any(attr.axis == axis for attr in op.get_attribute(Tensorwise))
