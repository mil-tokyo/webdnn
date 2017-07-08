from typing import Dict, Tuple, Type, List, Optional

from webdnn.graph import variable
from webdnn.graph.attribute import Attribute
from webdnn.graph.node import Node


class Operator(Node):
    """
    Operator a.k.a layer or function, is one of key component in DNN computation graph.

    Args:
        name (str): the name

    Attributes:
        inputs (dict of :class:`~webdnn.graph.variable.Variable`): input varibales
        outputs (dict of :class:`~webdnn.graph.variable.Variable`): output variable
    """
    inputs: Dict[str, "variable.Variable"]
    outputs: Dict[str, "variable.Variable"]

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self.inputs = {}
        self.outputs = {}

    def _get_input_name(self, var: "variable.Variable"):
        for name, v in self.inputs.items():
            if v is not var:
                continue

            return name

        else:
            raise KeyError(f"'{name}' is not input of {self}")

    def _get_output_name(self, var: "variable.Variable"):
        for name, v in self.outputs.items():
            if v is not var:
                continue

            return name

        else:
            raise KeyError(f"'{name}' is not output of {self}")

    def append_input(self, name: str, var: "variable.Variable"):
        """
        Append input variable

        Args:
            name(str): the name of input variable
            var(:class:`~webdnn.graph.variable.Variable`): the variable
        """
        # noinspection PyTypeChecker
        self.append_prev(var)

        self.inputs[name] = var
        var.input_to.add(self)

    def remove_input(self, var: "variable.Variable"):
        """
        Remove input variable

        Args:
            var(:class:`~webdnn.graph.variable.Variable`): the variable
        """
        # noinspection PyTypeChecker
        self.remove_prev(var)

        name = self._get_input_name(var)
        self.inputs.pop(name)
        var.input_to.remove(self)

    def replace_input(self, v_old: "variable.Variable", v_new: "variable.Variable"):
        """
        Replace input variable with other variable

        Args:
            v_old(:class:`~webdnn.graph.variable.Variable`): the variable which is removed
            v_new(:class:`~webdnn.graph.variable.Variable`): the variable which is appended
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

        name = self._get_input_name(v_old)
        self.remove_input(v_old)
        self.append_input(name, v_new)

    def append_output(self, name: str, var: "variable.Variable"):
        """
        Append output variable

        Args:
            name(str): the name of output variable
            var(:class:`~webdnn.graph.variable.Variable`): the variable
        """
        if var.output_from is not None:
            raise KeyError(f"{var} has been registered as f{var.output_from}'s output already.")

        # noinspection PyTypeChecker
        self.append_next(var)

        self.outputs[name] = var
        var.output_from = self

    def remove_output(self, var: "variable.Variable"):
        """
        Remove output variable

        Args:
            var(:class:`~webdnn.graph.variable.Variable`): the variable
        """
        # noinspection PyTypeChecker
        self.remove_next(var)

        name = self._get_output_name(var)
        self.outputs.pop(name)
        var.output_from = None

    def replace_output(self, v_old: "variable.Variable", v_new: "variable.Variable"):
        """
        Replace output variable with other variable

        Args:
            v_old(:class:`~webdnn.graph.variable.Variable`): the variable which is removed
            v_new(:class:`~webdnn.graph.variable.Variable`): the variable which is appended
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

        name = self._get_output_name(v_old)
        self.remove_output(v_old)
        self.append_output(name, v_new)

    def remove_all(self):
        """
        Remove all input and output variables
        """
        for _, v in list(self.inputs.items()):
            self.remove_input(v)

        for _, v in list(self.outputs.items()):
            self.remove_output(v)

    def replace(self, op_new: "Operator"):
        """
        Replace this operator with other operator. all variables connected with this operator will be disconnected and
        connected to the other operator.

        Args:
            op_new(:class:`~webdnn.graph.operator.Operator`): the new operator
        """
        inputs = dict(self.inputs)
        outputs = dict(self.outputs)

        self.remove_all()

        for name, var in inputs.items():
            op_new.append_input(name, var)

        for name, var in outputs.items():
            op_new.append_output(name, var)

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
