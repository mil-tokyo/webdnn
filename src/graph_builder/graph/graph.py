from typing import Dict, Set, List, Iterable

import numpy as np

from graph_builder.graph.attribute import Attribute


class Node:
    attributes: Set[Attribute] = set()

    def __init__(self):
        self.attributes = set(self.attributes)  # copy construction

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __str__(self):
        return self.__repr__()


class Operator(Node):
    name: str
    attributes: Set[Attribute] = []
    inputs: Dict[str, "Variable"]
    outputs: Dict[str, "Variable"]

    def __init__(self,
                 name: str,
                 parameters: Dict[str, object] = None,
                 inputs: Dict[str, "Variable"] = None,
                 outputs: Dict[str, "Variable"] = None):

        super().__init__()

        parameters = parameters if parameters is not None else {}
        inputs = inputs if inputs is not None else {}
        outputs = outputs if outputs is not None else {}

        self.name = name
        self.parameters = parameters
        self.inputs = inputs
        self.outputs = outputs

        for name, var in inputs.items():
            self.append_input(name, var)

        for name, var in outputs.items():
            self.append_input(name, var)

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
        self.inputs[name] = var
        var.input_to.add(self)

    def remove_input(self, var: "Variable"):
        name = self.get_input_name(var)
        self.inputs.pop(name)
        var.input_to.remove(self)

    def replace_input(self, v_old: "Variable", v_new: "Variable"):
        name = self.get_input_name(v_old)
        self.remove_input(v_old)
        self.append_input(name, v_new)

    def append_output(self, name: str, var: "Variable"):
        if var.output_from is not None:
            raise KeyError(f"{var} has been registered as f{var.output_from}'s output already.")

        self.outputs[name] = var
        var.output_from = self

    def remove_output(self, var: "Variable"):
        name = self.get_output_name(var)
        var = self.outputs.pop(name)
        var.output_from = None

    def replace_output(self, v_old: "Variable", v_new: "Variable"):
        name = self.get_output_name(v_old)
        self.remove_output(v_old)
        self.append_output(name, v_new)

    def __repr__(self):
        return f"""<{self.__class__.__name__} inputs={self.inputs}, outputs={self.outputs}>"""

    def __str__(self):
        return self.__repr__()

    def __call__(self, *args: Iterable["Variable"]) -> Iterable["Variable"]:
        raise NotImplementedError

    def dump(self):
        queue: List["Operator"] = [self]

        while len(queue) > 0:
            op = queue.pop(0)
            print(f"--------------------------------------------------------")
            print(f"  {op.__class__.__name__}")
            print(f"      In : {op.inputs}")
            print(f"      Out: {op.outputs}")

            for out in op.outputs.values():
                for next_op in out.input_to:
                    queue.append(next_op)


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
    axis_order: Attribute

    def __init__(self, shape: List[int], axis_order: Attribute):
        super().__init__()
        self.shape = list(shape)
        self.input_to = set()
        self.attributes.add(axis_order)
        self.axis_order = axis_order
        assert axis_order.ndim == len(self.shape)

    @property
    def size(self):
        return np.prod(self.shape)

    @property
    def ndim(self):
        return len(self.shape)

    @property
    def shape_dict(self):
        return self.axis_order.get_shape_dict(self)

    def __repr__(self):
        return f"<Variable shape={self.shape}, order=\"{self.axis_order.order_chars}\">"

    def __str__(self):
        return self.__repr__()

    def dump(self):
        queue: List["Operator"] = list(self.input_to)

        while len(queue) > 0:
            op = queue.pop(0)
            print(f"--------------------------------------------------------")
            print(f"  {op.__class__.__name__}")
            print(f"      In  : {op.inputs}")
            print(f"      Out : {op.outputs}")
            print(f"      Attr: {[attr.__name__ for attr in op.attributes]}")

            for out in op.outputs.values():
                for next_op in out.input_to:
                    queue.append(next_op)
