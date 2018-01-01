from typing import Dict, Tuple, Optional

from webdnn.graph import variable, graph
from webdnn.graph.node import Node


class Operator(Node):
    """Operator(name=None)

    Operator a.k.a layer or function in DNN computation graph.

    Args:
        name (str): the name. If :code:`None`, automatically generated name is used.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        self._inputs = {}  # type: Dict[str, "variable.Variable"]
        self._outputs = {}  # type: Dict[str, "variable.Variable"]

    def copy(self):
        """copy()

        Create new operator instance, which is initialized with parameters same as this operator.
        """
        # TODO: Is this correct?
        return self.__class__(None, **self.parameters)

    @property
    def inputs(self) -> Dict[str, "variable.Variable"]:
        """input variables"""
        return dict(self._inputs)

    @property
    def outputs(self) -> Dict[str, "variable.Variable"]:
        """output variables"""
        return dict(self._outputs)

    def get_input_name(self, var: "variable.Variable"):
        for name, v in self.inputs.items():
            if v is var:
                return name

        else:
            raise KeyError(f"'{var}' is not input of {self}")

    def get_output_name(self, var: "variable.Variable"):
        for name, v in self.outputs.items():
            if v is var:
                return name

        else:
            raise KeyError(f"'{var}' is not output of {self}")

    def append_input(self, name: str, var: "variable.Variable"):
        """append_input(name, var)

        Append input variable

        Args:
            name(str): the name of input variable
            var(:class:`~webdnn.Variable`): the variable
        """
        if name in self.inputs:
            raise KeyError(f"{name} is already used as key of input variable f{self.inputs[name]}.")

        self.append_prev(var)
        self._inputs[name] = var

    def remove_input(self, var: "variable.Variable"):
        """remove_input(var)

        Remove input variable

        Args:
            var(:class:`~webdnn.Variable`): the variable
        """
        if var not in self.prevs:
            raise KeyError(f"{var} is not registered in input variables.")

        name = self.get_input_name(var)

        self.remove_prev(var)
        self._inputs.pop(name)

    def replace_input(self, v_old: "variable.Variable", v_new: "variable.Variable", with_assert: bool = True):
        """replace_input(v_old, v_new)

        Replace input variable with other variable

        Args:
            v_old(:class:`~webdnn.Variable`): the variable which is removed
            v_new(:class:`~webdnn.Variable`): the variable which is appended
            with_assert (bool): If :code:`True`, it is checked whether shape and order is same as variable which will be removed
        """

        if with_assert:
            assert v_old.ndim == v_new.ndim, f"""
[operator.replace_input(v_old, v_new)] v_old and v_new must have same number of dimensions.
    (v_old.ndim) = {v_old.ndim}
    (v_new.ndim) = {v_new.ndim}"""
            assert v_old.order == v_new.order, f"""
[operator.replace_input(v_old, v_new)] v_old and v_new must be same data order.
    (v_old.order) = {v_old.order}
    (v_new.order) = {v_new.order}"""
            assert v_old.shape == v_new.shape, f"""
[operator.replace_input(v_old, v_new)] v_old and v_new must be same shape.
    (v_old.shape) = {v_old.shape}
    (v_new.shape) = {v_new.shape}"""

        name = self.get_input_name(v_old)
        self.remove_input(v_old)
        self.append_input(name, v_new)

    def append_output(self, name: str, var: "variable.Variable"):
        """append_output(name, var)

        Append output variable

        Args:
            name(str): the name of output variable
            var(:class:`~webdnn.Variable`): the variable
        """
        if name in self.outputs:
            raise KeyError(f"{name} is already used as key of output variable f{self.outputs[name]}.")
        if var.output_from is not None:
            raise KeyError(f"{var} has been registered as f{var.output_from}'s output already.")

        self.append_next(var)
        self._outputs[name] = var

    def remove_output(self, var: "variable.Variable"):
        """remove_output(var)

        Remove output variable

        Args:
            var(:class:`~webdnn.Variable`): the variable
        """
        if var not in self.nexts:
            raise KeyError(f"{var} is not registered in input variables.")
        name = self.get_output_name(var)

        self.remove_next(var)
        self._outputs.pop(name)

    def replace_output(self, v_old: "variable.Variable", v_new: "variable.Variable", with_assert: bool = True):
        """replace_output(v_old, v_new)

        Replace output variable with other variable

        Args:
            v_old(:class:`~webdnn.Variable`): the variable which is removed
            v_new(:class:`~webdnn.Variable`): the variable which is appended
            with_assert (bool): If :code:`True`, it is checked whether shape and order is same as variable which will be removed
        """

        if with_assert:
            assert v_old.ndim == v_new.ndim, f"""
[operator.replace_output(v_old, v_new)] v_old and v_new must have same number of dimensions.
    (v_old.ndim) = {v_old.ndim}
    (v_new.ndim) = {v_new.ndim}"""
            assert v_old.order == v_new.order, f"""
[operator.replace_output(v_old, v_new)] v_old and v_new must be same data order.
    (v_old.order) = {v_old.order}
    (v_new.order) = {v_new.order}"""
            assert v_old.shape == v_new.shape, f"""
[operator.replace_output(v_old, v_new)] v_old and v_new must be same shape.
    (v_old.shape) = {v_old.shape}
    (v_new.shape) = {v_new.shape}"""

        name = self.get_output_name(v_old)
        self.remove_output(v_old)
        self.append_output(name, v_new)

    def remove_all(self):
        """remove_all()

        Remove all input and output variables
        """
        for _, v in list(self.inputs.items()):
            self.remove_input(v)

        for _, v in list(self.outputs.items()):
            self.remove_output(v)

    def replace(self, op_new: "Operator"):
        """replace(op_new)

        Replace this operator by new operator. all variables connected with this operator will be disconnected and
        connected to the new operator.

        Args:
            op_new(:class:`~webdnn.Operator`): the new operator
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
        raise NotImplementedError(f"Operator.__call__ must be override: (self.__class__)={self.__class__.__name__}")

    def fold_constance(self, graph: "graph.Graph"):
        raise NotImplementedError(f"Operator.fold_constance must be override: (self.__class__)={self.__class__.__name__}")
