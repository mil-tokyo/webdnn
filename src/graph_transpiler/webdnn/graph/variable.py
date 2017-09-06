from typing import Union, List, Set, Tuple, Sequence

import webdnn.graph
from webdnn.graph import operator
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.node import Node
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.util.misc import mul


class Variable(Node):
    """Variable(shape, order)

    Data container class which is input to and output from operators.

    Variable supports basic unary and binary operations.

    .. code::

        x1 = Variable((2, 3), OrderNC)
        x2 = Variable((3, 2), OrderCN)
        h = x1 + x2
        y = abs(h)

        # variables are connected as follows:
        #
        #   x1 -+
        #       +-[ElementwiseAdd]-> h -[ElementwiseAbs]-> y
        #   x2 -+
    """

    def __init__(self, shape: Sequence[Union[int, Placeholder]], order: Order):
        super().__init__()

        assert order.ndim == len(shape), f"[Variable] order and shape are mismatched: order={order}, shape={shape}"

        self._shape = tuple(shape)  # type: Tuple[Union[int, Placeholder]]
        self._order = order  # type: Order

    @property
    def shape(self) -> Tuple[Union[int, Placeholder], ...]:
        """variable's shape"""
        return tuple(self._shape)

    @property
    def input_to(self) -> Set["operator.Operator"]:
        """operators which this variable is input to"""
        return set(self.nexts)

    @property
    def output_from(self) -> "operator.Operator":
        """operator which this variable is output from"""
        return None if len(self.prevs) == 0 else list(self.prevs)[0]

    @property
    def order(self) -> Order:
        """data order"""
        return self._order

    @property
    def name(self) -> str:
        """name of this variable"""
        return self.parameters["name"] if "name" in self.parameters else ""

    @name.setter
    def name(self, name: str):
        self.parameters["name"] = name

    @property
    def size(self) -> Union[int, Placeholder]:
        """number of elements"""
        return Placeholder.to_int(mul(self.shape))

    @property
    def ndim(self):
        """number of dimension"""
        return self.order.ndim

    @property
    def shape_dict(self) -> AxisKeyDict[Union[int, Placeholder]]:
        """dictionary of axis and shape size pairs"""
        return AxisKeyDict(self.order.axes, self.shape)

    @property
    def stride(self) -> List[Union[int, Placeholder]]:
        """stride size for each dimension"""
        return [mul(self.shape[i + 1:]) for i in range(self.ndim)]

    @property
    def stride_dict(self) -> AxisKeyDict[Union[int, Placeholder]]:
        """dictionary of axis and stride size pairs"""
        return AxisKeyDict(self.order.axes, self.stride)

    def copy(self) -> "Variable":
        return Variable(self.shape, self.order)

    def change_order(self, order: Order) -> "Variable":
        """change_order(order)

        Change variable order.

        When number of dimension will be increased, axes whose size is one are created.
        Conversely when number of dimension will be decreased, the size of axes which will be removed must be one.

        Args:
            order: new order
        """
        current_shape_dict = self.shape_dict
        new_shape = [current_shape_dict.get(axis, 1) for axis in order.axes]
        for axis, size in current_shape_dict.items():
            if axis not in order.axes:
                if Placeholder.check_resolved(size):
                    assert size == 1, "[Variable.change_order()] The size of axes which will be removed must be one: " \
                                      f"variable={self}, shape_dict[{axis}]={size}, new_order={order}."
        self._order = order
        self._shape = new_shape

        return self

    def replace(self, new_variable: "Variable"):
        """replace(new_variable)

        Replace this variable in graph by specified new variable.

        All operators connected with this variable are disconnected and re-connected to new variable with same name.

        Args:
            new_variable (:class:`~webdnn.Variable`): new variable
        """
        if self.output_from:
            self.output_from.replace_output(self, new_variable)

        for op in list(self.input_to):
            op.replace_input(self, new_variable)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} shape={self.shape}, order={self.order}>"

    def __str__(self):
        return self.__repr__()

    # Unary operators
    def __pos__(self) -> "Variable":
        return webdnn.graph.operators.scalar_affine.ScalarAffine(None, scale=+1, bias=0)(self)[0]

    def __neg__(self) -> "Variable":
        return webdnn.graph.operators.scalar_affine.ScalarAffine(None, scale=-1, bias=0)(self)[0]

    def __abs__(self) -> "Variable":
        return webdnn.graph.operators.abs.Abs(None)(self)[0]

    # Binary operators
    def __add__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'")

    def __radd__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(other).__name__}' and '{type(self).__name__}'")

    def __sub__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, -other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(self, -other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for -: '{type(self).__name__}' and '{type(other).__name__}'")

    def __rsub__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, other)(-self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(other, -self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for -: '{type(other).__name__}' and '{type(self).__name__}'")

    def __mul__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_mul.ElementwiseMul(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for *: '{type(self).__name__}' and '{type(other).__name__}'")

    def __rmul__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_mul.ElementwiseMul(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for *: '{type(other).__name__}' and '{type(self).__name__}'")

    def __truediv__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, 1 / other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_div.ElementwiseDiv(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for /: '{type(self).__name__}' and '{type(other).__name__}'")

    def __rtruediv__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, other)(self ** -1)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_div.ElementwiseDiv(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for *: '{type(other).__name__}' and '{type(self).__name__}'")

    def __pow__(self, power, modulo=None) -> "Variable":
        if modulo is not None:
            raise NotImplementedError("Variable.__pow__ is not supported modulo argument")

        elif isinstance(power, (int, float)):
            return webdnn.graph.operators.scalar_pow.ScalarPow(None, power)(self)[0]

        elif isinstance(power, Variable):
            return webdnn.graph.operators.elementwise_pow.ElementwisePow(None)(self, power)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for ** or pow: '{type(self).__name__}' and '{type(power).__name__}'")

    def __rpow__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            # FIXME
            raise TypeError(f"unsupported operand type(s) for ** or pow: '{type(other).__name__}' and '{type(self).__name__}'")

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_pow.ElementwisePow(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for ** or pow: '{type(other).__name__}' and '{type(self).__name__}'")
