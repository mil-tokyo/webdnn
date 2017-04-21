from typing import Dict, Set, List, Iterable, Type

import numpy as np

from graph_builder.graph.attribute import Attribute


class Node:
    attributes: Set[Type[Attribute]] = set()
    parameters: Dict[str, any]

    def __init__(self, parameters: Dict[str, any] = None):
        self.parameters = parameters if parameters is not None else {}
        self.attributes = set(self.attributes)  # copy construction

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return self.__repr__()


class Operator(Node):
    name: str
    attributes: Set[Type[Attribute]] = []
    inputs: Dict[str, "Variable"]
    outputs: Dict[str, "Variable"]

    def __init__(self,
                 name: str,
                 parameters: Dict[str, object] = None):

        super().__init__(parameters)

        self.name = name
        self.parameters = parameters
        self.inputs = {}
        self.outputs = {}

    def get_input_name(self, var: "Variable"):
        for name, v in self.inputs.items():
            if v is not var:
                continue

            return name

        else:
            raise KeyError(f"'{name}' is not input of {self}")

    def get_output_name(self, var: "Variable"):
        for name, v in self.outputs.items():
            if v is not var:
                continue

            return name

        else:
            raise KeyError(f"'{name}' is not output of {self}")

    def append_input(self, name: str, var: "Variable"):
        """
        入力変数を追加する
        """
        self.inputs[name] = var
        var.input_to.add(self)

    def remove_input(self, var: "Variable"):
        """
        入力変数を解除する
        """
        name = self.get_input_name(var)
        self.inputs.pop(name)
        var.input_to.remove(self)

    def replace_input(self, v_old: "Variable", v_new: "Variable"):
        """
        入力変数を置き換える
        """
        assert v_old.ndim == v_new.ndim, \
            "[operator.replace_input(v_old, v_new)] v_old and v_new must have same number of dimensions." + \
            f"actual: v_old.ndim = {v_old.ndim}, v_new.ndim = {v_new.ndim}"
        assert v_old.axis_order == v_new.axis_order, \
            "[operator.replace_input(v_old, v_new)] v_old and v_new must be same data order." + \
            f"actual: v_old.axis_order = {v_old.axis_order}, v_new.axis_order = {v_new.axis_order}"
        assert v_old.shape == v_new.shape, \
            "[operator.replace_input(v_old, v_new)] v_old and v_new must be same shape." + \
            f"actual: v_old.axis_order = {v_old.shape}, v_new.axis_order = {v_new.shape}"

        name = self.get_input_name(v_old)
        self.remove_input(v_old)
        self.append_input(name, v_new)

    def append_output(self, name: str, var: "Variable"):
        """
        出力変数を追加する
        """
        if var.output_from is not None:
            raise KeyError(f"{var} has been registered as f{var.output_from}'s output already.")

        self.outputs[name] = var
        var.output_from = self

    def remove_output(self, var: "Variable"):
        """
        出力変数を解除する
        """
        name = self.get_output_name(var)
        self.outputs.pop(name)
        var.output_from = None

    def replace_output(self, v_old: "Variable", v_new: "Variable"):
        """
        出力変数を置き換える
        """
        assert v_old.ndim == v_new.ndim, \
            "[operator.replace_output(v_old, v_new)] v_old and v_new must have same number of dimensions." + \
            f"actual: v_old.ndim = {v_old.ndim}, v_new.ndim = {v_new.ndim}"
        assert v_old.axis_order == v_new.axis_order, \
            "[operator.replace_output(v_old, v_new)] v_old and v_new must be same data order." + \
            f"actual: v_old.axis_order = {v_old.axis_order}, v_new.axis_order = {v_new.axis_order}"
        assert v_old.shape == v_new.shape, \
            "[operator.replace_output(v_old, v_new)] v_old and v_new must be same shape." + \
            f"actual: v_old.axis_order = {v_old.shape}, v_new.axis_order = {v_new.shape}"

        name = self.get_output_name(v_old)
        self.remove_output(v_old)
        self.append_output(name, v_new)

    def remove_all(self):
        """
        全ての変数の接続を解除する
        """
        for _, v in list(self.inputs.items()):
            self.remove_input(v)

        for _, v in list(self.outputs.items()):
            self.remove_output(v)

    def __repr__(self):
        return f"""<{self.__class__.__name__} inputs={self.inputs}, outputs={self.outputs}>"""

    def __str__(self):
        return self.__repr__()

    def __call__(self, *args: Iterable["Variable"]) -> Iterable["Variable"]:
        raise NotImplementedError


class Variable(Node):
    """
    レイヤー間で受け渡される変数
    名前で識別される
    現在のところ、float32型(4byte/element)を想定している
    shapeはタプルで、その順序はAttribute(OrderNC etc)に依存
    """

    shape: List[int]
    input_to: Set[Operator]
    output_from: Operator = None
    axis_order: Type[Attribute]  # FIXME: Attribute -> AxisOrder

    def __init__(self, shape: List[int], axis_order: Type[Attribute]):
        from graph_builder.graph.variables import attributes as VA  # FIXME import order
        assert issubclass(axis_order, VA.AxisOrder)
        super().__init__()
        self.shape = list(shape)
        self.input_to = set()
        self.attributes.add(axis_order)
        self.axis_order = axis_order
        assert axis_order.ndim == len(self.shape)

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
        return self.axis_order.get_shape_dict(self)

    def change_axis_order(self, axis_order: Type[Attribute]):
        from graph_builder.graph.variables import attributes as VA  # FIXME import order
        assert issubclass(axis_order, VA.AxisOrder)
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
        from graph_builder.graph.operators.compose import VariableAlias  # FIXME

        if isinstance(base, VariableAlias):
            base = base.original

        if base.output_from is not None:
            raise ValueError(f"[Variabe.merge(base)] Base variable {base} must not has 'output_from' operator.")

        for op in list(base.input_to):  # type: Operator
            op.replace_input(base, self)
