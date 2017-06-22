from typing import Dict, Tuple, Type, List

from webdnn.graph import variable
from webdnn.graph.attribute import Attribute
from webdnn.graph.node import Node


# FIXME: DOCS
class Operator(Node):
    inputs: Dict[str, "variable.Variable"]
    outputs: Dict[str, "variable.Variable"]

    def __init__(self, name: str):
        super().__init__(name)
        self.inputs = {}
        self.outputs = {}

    def get_input_name(self, var: "variable.Variable"):
        for name, v in self.inputs.items():
            if v is not var:
                continue

            return name

        else:
            raise KeyError(f"'{name}' is not input of {self}")

    def get_output_name(self, var: "variable.Variable"):
        for name, v in self.outputs.items():
            if v is not var:
                continue

            return name

        else:
            raise KeyError(f"'{name}' is not output of {self}")

    def append_input(self, name: str, var: "variable.Variable"):
        """
        入力変数を追加する
        """
        # noinspection PyTypeChecker
        self.append_prev(var)

        self.inputs[name] = var
        var.input_to.add(self)

    def remove_input(self, var: "variable.Variable"):
        """
        入力変数を解除する
        """
        # noinspection PyTypeChecker
        self.remove_prev(var)

        name = self.get_input_name(var)
        self.inputs.pop(name)
        var.input_to.remove(self)

    def replace_input(self, v_old: "variable.Variable", v_new: "variable.Variable"):
        """
        入力変数を置き換える
        """
        assert v_old.ndim == v_new.ndim, \
            "[operator.replace_input(v_old, v_new)] v_old and v_new must have same number of dimensions." + \
            f"actual: v_old.ndim = {v_old.ndim}, v_new.ndim = {v_new.ndim}"
        assert v_old.order == v_new.order, \
            "[operator.replace_input(v_old, v_new)] v_old and v_new must be same data order." + \
            f"actual: v_old.order = {v_old.order}, v_new.order = {v_new.order}"
        assert v_old.shape == v_new.shape, \
            "[operator.replace_input(v_old, v_new)] v_old and v_new must be same shape." + \
            f"actual: v_old.order = {v_old.shape}, v_new.order = {v_new.shape}"

        name = self.get_input_name(v_old)
        self.remove_input(v_old)
        self.append_input(name, v_new)

    def append_output(self, name: str, var: "variable.Variable"):
        """
        出力変数を追加する
        """
        if var.output_from is not None:
            raise KeyError(f"{var} has been registered as f{var.output_from}'s output already.")

        # noinspection PyTypeChecker
        self.append_next(var)

        self.outputs[name] = var
        var.output_from = self

    def remove_output(self, var: "variable.Variable"):
        """
        出力変数を解除する
        """
        # noinspection PyTypeChecker
        self.remove_next(var)

        name = self.get_output_name(var)
        self.outputs.pop(name)
        var.output_from = None

    def replace_output(self, v_old: "variable.Variable", v_new: "variable.Variable"):
        """
        出力変数を置き換える
        """
        assert v_old.ndim == v_new.ndim, \
            "[operator.replace_output(v_old, v_new)] v_old and v_new must have same number of dimensions." + \
            f"actual: v_old.ndim = {v_old.ndim}, v_new.ndim = {v_new.ndim}"
        assert v_old.order == v_new.order, \
            "[operator.replace_output(v_old, v_new)] v_old and v_new must be same data order." + \
            f"actual: v_old.order = {v_old.order}, v_new.order = {v_new.order}"
        assert v_old.shape == v_new.shape, \
            "[operator.replace_output(v_old, v_new)] v_old and v_new must be same shape." + \
            f"actual: v_old.shape = {v_old.shape}, v_new.shape = {v_new.shape}"

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

    def replace(self, new_op: "Operator"):
        """
        演算を置き換える
        """
        inputs = dict(self.inputs)
        outputs = dict(self.outputs)

        self.remove_all()

        for name, var in inputs.items():
            new_op.append_input(name, var)

        for name, var in outputs.items():
            new_op.append_output(name, var)

    def __repr__(self):
        return f"""<{self.__class__.__name__} inputs={self.inputs}, outputs={self.outputs}>"""

    def __str__(self):
        return self.__repr__()

    def __call__(self, *args, **kwargs) -> Tuple["variable.Variable"]:
        pass

    def get_attribute(self, Attr: Type[Attribute]) -> List[Attribute]:
        return [attr for attr in self.attributes if isinstance(attr, Attr)]

    def has_attribute(self, Attr: Type[Attribute]) -> bool:
        return len(self.get_attribute(Attr)) > 0
