from typing import Union, Dict, List, Set, Iterable

import webdnn.graph
from webdnn.graph import operator
from webdnn.graph.axis import Axis
from webdnn.graph.node import Node
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.util.misc import mul


class Variable(Node):
    """
    Variables input to / output from operators.

    Attrs:
        shape (list of int or Placeholder): shape of the variable.
        order (Order): Data order such as OrderNHWC, OrderNC, and so on.
        input_to (set of Operator): operators to which this variable is input
        output_from (Operator): operator which generates this variable
    """
    shape: List[Union[int, Placeholder]]
    order: Order
    input_to: Set["operator.Operator"]
    output_from: "operator.Operator"

    def __init__(self, shape: Iterable[Union[int, Placeholder]], order: Order):
        super().__init__()

        self.shape = list(shape)
        self.input_to = set()
        self.output_from = None
        self.order = order

        assert self.order.ndim == len(self.shape), "[Variable] order and shape are mismatched:"
        f"order={order}, shape={shape}"

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
    def shape_dict(self) -> Dict[Axis, Union[int, Placeholder]]:
        """dictionary of axis and shape size pairs"""
        return dict(zip(self.order.axes, self.shape))

    def change_order(self, order: Order) -> "Variable":
        """Change variable order

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
                    assert size == 1, "[Variable.change_order()] The size of axes which will be removed must be one:"
                    f"variable={self}, shape_dict[{axis}]={size}."
        self.order = order
        self.shape = new_shape

        return self

    def replace(self, new_variable: "Variable"):
        if self.output_from:
            self.output_from.replace_output(self, new_variable)

        for op in list(self.input_to):  # type: operator.Operator
            op.replace_input(self, new_variable)

    def __repr__(self):
        order_repr = ''.join(map(lambda e: e.name, self.order.axes))
        return f"<{self.__class__.__name__} {self.name} shape={self.shape}, order=\"{order_repr}\">"

    def __str__(self):
        return self.__repr__()

    # Unary operators
    def __pos__(self):
        return webdnn.graph.operators.scalar_affine.ScalarAffine(None, scale=+1, bias=0)(self)[0]

    def __neg__(self):
        return webdnn.graph.operators.scalar_affine.ScalarAffine(None, scale=-1, bias=0)(self)[0]

    def __abs__(self):
        return webdnn.graph.operators.abs.Abs(None)(self)[0]

    # Binary operators
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Variable' and '{type(other)}'")

    def __radd__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(other)}' and 'Variable'")

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, -other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(self, -other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for -: 'Variable' and '{type(other)}'")

    def __rsub__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_add.ScalarAdd(None, other)(-self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_add.ElementwiseAdd(None)(other, -self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for -: '{type(other)}' and 'Variable'")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_mul.ElementwiseMul(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for *: 'Variable' and '{type(other)}'")

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_mul.ElementwiseMul(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for *: '{type(other)}' and 'Variable'")

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, 1 / other)(self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_div.ElementwiseDiv(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for /: 'Variable' and '{type(other)}'")

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            return webdnn.graph.operators.scalar_mul.ScalarMul(None, other)(self ** -1)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_div.ElementwiseDiv(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for *: '{type(other)}' and 'Variable'")

    def __pow__(self, power, modulo=None):
        if modulo is not None:
            raise NotImplementedError("Variable.__pow__ is not supported modulo argument")

        elif isinstance(power, (int, float)):
            return webdnn.graph.operators.scalar_pow.ScalarPow(None, power)(self)[0]

        elif isinstance(power, Variable):
            return webdnn.graph.operators.elementwise_pow.ElementwisePow(None)(self, power)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for ** or pow: 'Variable' and '{type(other)}'")

    def __rpow__(self, other):
        if isinstance(other, (int, float)):
            # FIXME
            raise TypeError(f"unsupported operand type(s) for ** or pow: '{type(other)}' and 'Variable'")

        elif isinstance(other, Variable):
            return webdnn.graph.operators.elementwise_pow.ElementwisePow(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for ** or pow: '{type(other)}' and 'Variable'")
