from typing import Union, List, Set, Tuple, Sequence

import numpy as np

import webdnn.graph
from webdnn.graph import operator
from webdnn.graph.axis import AxisKeyDict, Axis
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
        #       +-[ElementwiseAdd]-> h -[Abs]-> y
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
        return tuple(Placeholder.to_int(v) for v in self._shape)

    @property
    def input_to(self) -> Set["operator.Operator"]:
        """operators which this variable is input to"""
        # noinspection PyTypeChecker
        return set(self.nexts)

    @property
    def output_from(self) -> "operator.Operator":
        """operator which this variable is output from"""
        # noinspection PyTypeChecker
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

    def change_order(self, order: Order) -> "Variable":
        """change_order_statement(order)

        Change variable order.

        When number of dimension will be increased, axes whose size is one are created.
        Conversely when number of dimension will be decreased, the size of axes which will be removed must be one.

        Args:
            order: new order
        """
        old_shape_dict = self.shape_dict
        new_shape = [old_shape_dict.get(axis, 1) for axis in order.axes]
        for axis, size in old_shape_dict.items():
            if axis not in order.axes:
                if Placeholder.check_resolved(size):
                    assert size == 1, f"""
[Variable.change_order()] The size of axes which will be removed must be one:
    (variable) = {self}
    (shape[{axis}]) = {size}
    (new order) = {order}
"""
        self._order = order
        self._shape = new_shape

        return self

    def replace(self, new_variable: "Variable", with_assert: bool = True):
        """replace(new_variable)

        Replace this variable in graph by specified new variable.

        All operators connected with this variable are disconnected and re-connected to new variable with same name.

        Args:
            new_variable (:class:`~webdnn.Variable`): new variable
            with_assert (bool): If :code:`True`, it is checked whether shape and order is same as variable which will be removed
        """
        if self.output_from:
            self.output_from.replace_output(self, new_variable, with_assert=with_assert)

        for op in list(self.input_to):
            op.replace_input(self, new_variable, with_assert=with_assert)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name} shape={self.shape}, order={self.order}>"

    def __str__(self):
        return self.__repr__()

    # Unary operators

    def __pos__(self) -> "Variable":
        return webdnn.graph.operators.scalar_mul.ScalarMul(None, value=+1)(self)[0]

    def __neg__(self) -> "Variable":
        return webdnn.graph.operators.scalar_mul.ScalarMul(None, value=-1)(self)[0]

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
            other = webdnn.graph.variables.constant_variable.ConstantVariable(np.full(self.shape, other), self.order)
            return webdnn.graph.operators.elementwise_pow.ElementwisePow(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for ** or pow: '{type(other).__name__}' and '{type(self).__name__}'")

    def __gt__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            other = webdnn.graph.variables.constant_variable.ConstantVariable(np.full(self.shape, other), self.order)
            return webdnn.graph.operators.greater.Greater(None)(self, other)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.greater.Greater(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for >: '{type(self).__name__}' and '{type(other).__name__}'")

    def __ge__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            other = webdnn.graph.variables.constant_variable.ConstantVariable(np.full(self.shape, other), self.order)
            return webdnn.graph.operators.greater_equal.GreaterEqual(None)(self, other)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.greater_equal.GreaterEqual(None)(self, other)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for >=: '{type(self).__name__}' and '{type(other).__name__}'")

    def __lt__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            other = webdnn.graph.variables.constant_variable.ConstantVariable(np.full(self.shape, other), self.order)
            return webdnn.graph.operators.greater.Greater(None)(other, self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.greater.Greater(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for <: '{type(self).__name__}' and '{type(other).__name__}'")

    def __le__(self, other) -> "Variable":
        if isinstance(other, (int, float)):
            other = webdnn.graph.variables.constant_variable.ConstantVariable(np.full(self.shape, other), self.order)
            return webdnn.graph.operators.greater_equal.GreaterEqual(None)(other, self)[0]

        elif isinstance(other, Variable):
            return webdnn.graph.operators.greater_equal.GreaterEqual(None)(other, self)[0]

        else:
            raise TypeError(f"unsupported operand type(s) for <=: '{type(self).__name__}' and '{type(other).__name__}'")

    def __getitem__(self, slices) -> "Variable":
        slices = list(slices) if isinstance(slices, Sequence) else [slices]

        if Ellipsis in slices:
            ellipsis_position = slices.index(Ellipsis)
            slices.remove(Ellipsis)
        else:
            ellipsis_position = len(slices)

        num_new_axis = slices.count(None)
        while len(slices) - num_new_axis < self.ndim:
            slices.insert(ellipsis_position, slice(None))

        x_axis_index = 0
        indices = AxisKeyDict()
        for index in slices:
            if isinstance(index, (slice, int)):
                indices[self.order.axes[x_axis_index]] = index
                x_axis_index += 1

            elif index is None:
                indices[Axis()] = None

            else:
                raise TypeError("Variable indices must be sequence of integers, slices, ellipsis, or None")

        return webdnn.graph.operators.slice.Slice(None, indices=indices)(self)[0]

    # Utility functions

    def reshape(self, shape: Sequence[Union[int, Placeholder]], order: Order) -> "Variable":
        """reshape(shape, order)
        Reshape into specified order and shape. This is alias of follow codes.

        .. code::

            Reshape(None, in_order=v.order,
                          out_order=order,
                          out_shape=shape)(v)[0]

        Args:
            shape (tuple of int): shape
            order (:class:`~Order`): order

        Returns:
            (:class:`~Variable`) new variable which has specified order and shape
        """
        ret, = webdnn.graph.operators.reshape.Reshape(None, in_order=self.order, out_order=order, out_shape=shape)(self)
        return ret

    def reshape_like(self, other: "Variable") -> "Variable":
        """reshape(shape, order)
        Reshape into same order and shape as :code:`other`. This is alias of follow codes.

        .. code::

            Reshape(None, in_order=v.order,
                          out_order=other.order,
                          out_shape=other.shape)(v)[0]

        Args:
            other (:class:`~Variable`): variable

        Returns:
            (:class:`~Variable`) new variable which has same order and shape as :code:`other`
        """
        ret, = webdnn.graph.operators.reshape.Reshape(None, in_order=self.order, out_order=other.order, out_shape=other.shape)(self)
        return ret

    def expand_dims(self, axis: Axis, index: int = -1) -> "Variable":
        """expand_dims(shape, axis, index)
        Insert new axis whose size is 1. This is alias of follow codes.

        .. code::

            new_axes = list(v.order.axes)
            new_axes.insert(index, axis)
            Reshape(None, in_order=v.order,
                          out_order=Order(new_axes),
                          out_shape=[1 if a == axis else self.shape_dict[a] for a in new_axes])(v)[0]

        Args:
            axis (:class:`~Axis`): inserted axis
            index (int, optional): insert position, As default, inserted at last.

        Returns:
            (:class:`~Variable`) expanded variable
        """
        if index < 0:
            index += self.ndim + 1
        new_axes = list(self.order.axes)
        new_axes.insert(index, axis)
        return self.reshape(shape=[1 if a == axis else self.shape_dict[a] for a in new_axes], order=Order(new_axes))

    def squeeze(self, axis: Union[Axis, Sequence[Axis]] = None) -> "Variable":
        """expand_dims(shape, axis, index)
        Remove axis whose size is 1. This is alias of follow codes.

        .. code::

            new_axes = list(v.order.axes)
            new_axes.remove(axis)
            Reshape(None, in_order=v.order,
                          out_order=Order(new_axes),
                          out_shape=[self.shape_dict[a] for a in new_axes])(v)[0]

        Args:
            axis (:class:`~Axis` or sequence of Axis, optional): removed axis.
                As default, all axes whose size are 1 is removed.

        Returns:
            (:class:`~Variable`) squeezed variable
        """
        new_axes = list(self.order.axes)
        if axis is None:
            for axis in self.order.axes:
                if self.shape_dict[axis] == 1:
                    new_axes.remove(axis)
        else:
            if isinstance(axis, Sequence):
                for a in axis:
                    new_axes.remove(a)
            else:
                new_axes.remove(axis)

        return self.reshape(shape=[self.shape_dict[a] for a in new_axes], order=Order(new_axes))

    def combine_axes(self, axes: Sequence[Axis], axis: Axis) -> "Variable":
        """combine_axes(shape, axes, axis)
        Combine some axes into one axis. Combined axes must be adjacent

        .. code::

            x = Variable([2, 3, 4, 5], OrderNHWC)

            y = x.combine_axes([Axis.W, Axis.H], Axis.W)
            # # same as follow code. Note that in_order is OrderNWHC, not OrderNHWC, because "axes" parameter is [W, H].
            # y, = Reshape(None, in_order=OrderNWHC, out_order=OrderNWC, out_shape=[2, 12, 5])(x)

            print(y.shape, y.order)
            >>> "[2, 12, 5]", "[N, H, C]"

        Args:
            axes (sequence of :class:`~Axis`): Axes which are combined. All axes must be contained in original variable.
            axis (:class:`~Axis`): Axis created from `axes`. If new axis is specified, which is inserted at last.

        Returns:
            (:class:`~Variable`) reshaped variable
        """
        # check if all combined axes are adjacent
        i_max = 0
        i_min = self.ndim
        for combined_axis in axes:
            i = self.order.axes_dict[combined_axis]
            i_max = max(i_max, i)
            i_min = min(i_min, i)

        assert i_max - i_min + 1 == len(axes), f"""
All combined axes must be adjacent:
    (order) = {self.order}
    (combined axes) = {axes}"""

        # construct in_order, out_order and out_shape
        in_order = Order(self.order.axes[:i_min] + tuple(axes) + self.order.axes[i_max + 1:])

        out_axes = list(self.order.axes)
        out_shape_dict = AxisKeyDict(self.shape_dict)
        if axis not in out_shape_dict:
            out_shape_dict[axis] = 1
            out_axes.insert(i_min, axis)

        for combined_axis in axes:
            if combined_axis == axis:
                continue

            out_shape_dict[axis] *= out_shape_dict[combined_axis]
            out_axes.remove(combined_axis)

        out_order = Order(out_axes)

        return webdnn.graph.operators.reshape.Reshape(None,
                                                      in_order=in_order,
                                                      out_order=out_order,
                                                      out_shape=[out_shape_dict[a] for a in out_axes])(self)[0]

    def transpose(self, order: Order) -> "Variable":
        """transpose(shape, order)
        Transpose into specified order. This is alias of `Transpose(None)(v)[0].change_order_statement(order)`

        Args:
            order (:class:`~Order`): order

        Returns:
            (:class:`~Variable`) new variable which has specified order
        """
        ret, = webdnn.graph.operators.transpose.Transpose(None)(self)
        ret.change_order(order)
        return ret

    def transpose_like(self, other: "Variable") -> "Variable":
        """reshape(shape, order)
        Transpose into same order as :code:`other`. This is alias of `Transpose(None)(v)[0].change_order_statement(other.order)`

        Args:
            other (:class:`~Variable`): variable

        Returns:
            (:class:`~Variable`) new variable which has same order as :code:`other`
        """
        ret, = webdnn.graph.operators.transpose.Transpose(None)(self)
        ret.change_order(other.order)
        return ret

    def reinterpret_axes(self, order: Order) -> "Variable":
        """reshape(shape, order)
        Reinterpret axes. This is alias of `ReinterpretAxes(None, v.order, order)(v)[0]`.

        Args:
            order (:class:`~Order`): new order

        Returns:
            (:class:`~Variable`) new variable which has same shape of original variable, but its order is :code:`order`.
        """
        ret, = webdnn.graph.operators.reinterpret_axis.ReinterpretAxis(None, in_order=self.order, out_order=order)(self)
        return ret
