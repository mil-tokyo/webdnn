from typing import Type, Iterable

import numpy as np

from graph_builder.graph.interface import IVariable
from graph_builder.graph.node import Node
from graph_builder.graph.variables.attributes.order import AxisOrder


class Variable(Node, IVariable):
    """
    レイヤー間で受け渡される変数
    名前で識別される
    現在のところ、float32型(4byte/element)を想定している
    shapeはタプルで、その順序はAttribute(OrderNC etc)に依存
    """

    def __init__(self, shape: Iterable[int], axis_order: Type[AxisOrder]):
        super().__init__()

        self.shape = list(shape)
        self.input_to = set()
        self.output_from = None
        self.axis_order = axis_order

        self.attributes.add(axis_order)

        assert self.axis_order.ndim == len(self.shape)

    @property
    def name(self):
        return self.parameters["name"] if "name" in self.parameters else ""

    @name.setter
    def name(self, name: str):
        self.parameters["name"] = name

    @property
    def size(self):
        # noinspection PyTypeChecker
        return int(np.prod(self.shape))

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def shape_dict(self):
        return dict(zip(self.axis_order.axes, self.shape))

    def change_axis_order(self, axis_order: Type[AxisOrder]):
        # 次元数を減らす時は、なくなる次元のサイズが1のときだけOK
        # 増える次元は、サイズ1
        current_shape_dict = self.shape_dict
        new_shape = [current_shape_dict.get(axis, 1) for axis in axis_order.axes]
        for axis, size in current_shape_dict.items():
            if axis not in axis_order.axes:
                assert size == 1
        self.axis_order = axis_order
        self.shape = new_shape

    def __repr__(self):
        order_repr = ''.join(map(lambda e: e.name, self.axis_order.axes))
        return f"<Variable shape={self.shape}, order=\"{order_repr}\">"

    def __str__(self):
        return self.__repr__()

    def merge(self, base: "Variable"):
        """
        baseへselfをマージする

        ```
        X --[OP1]-->tmp

                    base--[OP2]-->Y
        ```

        があったときに `tmp.merge(base)` をすると

        ```
        X --[OP1]-->tmp-->[OP2-->Y
        ```

        となる
        :param base: 
        :return: 
        """
        if base.output_from is not None:
            raise ValueError(f"[Variable.merge(base)] Base variable {base} must not has 'output_from' operator.")

        for op in list(base.input_to):
            op.replace_input(base, self)
