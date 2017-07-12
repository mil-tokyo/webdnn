from typing import Optional, List

import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.operator import Operator
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


# FIXME: improve documentation
from webdnn.util.misc import mul


class Transpose(Elementwise):
    """Transposition. Doing nothing in frontend level,
    and do memory transposition in backend if input / output variable order differs.
    This layer is inserted in optimizer to support layers which accepts certain order.

    Args:
        name (str): Operator name.
    """
    pass
