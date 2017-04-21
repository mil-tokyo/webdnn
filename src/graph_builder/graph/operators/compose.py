from typing import Iterable, Set, List, Type

from graph_builder.graph.interface import IVariable
from graph_builder.graph.operator import Operator
from graph_builder.graph.variables.attributes.order import AxisOrder


class VariableAlias(IVariable):
    link_to: IVariable
    axis_order: Type[AxisOrder]

    # noinspection PyMissingConstructor
    def __init__(self, var: IVariable):
        self.link_to = var
        self.input_to = set()
        self.output_from = None

    @property
    def size(self):
        return self.original.size

    @property
    def shape(self):
        return self.original.shape

    @property
    def ndim(self):
        return self.original.ndim

    @property
    def shape_dict(self):
        return self.original.shape_dict

    @property
    def axis_order(self):
        return self.original.axis_order

    def change_axis_order(self, axis_order: Type[AxisOrder]):
        return self.original.change_axis_order(axis_order)

    def __repr__(self):
        return self.original.__repr__()

    def __str__(self):
        return self.original.__str__()

    @property
    def parameters(self):
        return self.original.parameters

    @property
    def original(self):
        return self.link_to.original if isinstance(self.link_to, VariableAlias) else self.link_to

    def dump(self):
        return self.original.dump()

    def merge(self, base: IVariable) -> None:
        self.original.merge(base)

    @property
    def name(self) -> str:
        return self.original.name


class Compose(Operator):
    input_to: Set[Operator]
    inputs_alias: Set[VariableAlias]
    outputs_alias: Set[VariableAlias]

    def __init__(self, name: str = "composed"):
        super(Compose, self).__init__(name)
        self.inputs_alias = set()
        self.outputs_alias = set()

    def __call__(self, *args: Iterable[IVariable]) -> Iterable[IVariable]:
        raise NotImplementedError

    @classmethod
    def compose_ops(cls, name: str, ops: Iterable[Operator]):
        composite = Compose(name)

        inputs_or_hiddens: Set[IVariable] = set()
        outputs_or_hiddens: Set[IVariable] = set()

        for op in ops:
            inputs_or_hiddens.update(op.inputs.values())
            outputs_or_hiddens.update(op.outputs.values())

        inputs: Set[IVariable] = inputs_or_hiddens.difference(outputs_or_hiddens)
        outputs: Set[IVariable] = outputs_or_hiddens.difference(inputs_or_hiddens)

        for i, var in enumerate(inputs):
            alias = VariableAlias(var)
            composite.inputs_alias.add(alias)

            old_input_to = set(var.input_to)
            for op in old_input_to:  # type: Operator
                if op in ops:
                    op.replace_input(var, alias)
                    composite.append_input(f"in{i}", var)

        for i, var in enumerate(outputs):
            alias = VariableAlias(var)
            composite.outputs_alias.add(alias)

            var.output_from.replace_output(var, alias)
            composite.append_output(f"out{i}", var)

        return composite

    @classmethod
    def compose_with_vars(cls, name: str, inputs: Iterable[IVariable], outputs: Iterable[IVariable]) -> "Compose":
        # グラフを辿って必要なopsを全て取ってくる
        inputs = set(inputs)
        var_queue: List[IVariable] = list(outputs)
        ops: Set[Operator] = set()

        while len(var_queue) > 0:
            var = var_queue.pop(0)
            op = var.output_from
            if op is None or op in ops:
                continue

            ops.add(op)
            for var in op.inputs.values():
                if var in inputs:
                    continue

                var_queue.append(var)

        return Compose.compose_ops(name, ops)

    def decompose(self):
        # エイリアスを元に戻す
        for alias in self.inputs_alias:
            var = alias.link_to
            self.remove_input(var)
            ops = set(alias.input_to)
            for op in ops:
                op.replace_input(alias, var)
        self.inputs_alias = set()

        for alias in self.outputs_alias:
            var = alias.link_to
            self.remove_output(var)
            alias.output_from.replace_output(alias, var)

        self.outputs_alias = set()
