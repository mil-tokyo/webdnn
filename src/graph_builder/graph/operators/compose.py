from typing import Iterable, Set, List, Type

from graph_builder.graph.attribute import Attribute
from graph_builder.graph.graph import Operator, Variable


class VariableAlias(Variable):
    link_to: Variable
    axis_order: Type[Attribute]  # FIXME: Attribute -> AxisOrder

    # noinspection PyMissingConstructor
    def __init__(self, var: Variable):
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

    def change_axis_order(self, axis_order: Type[Attribute]):
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


class Compose(Operator):
    input_to: Set[Operator]
    inputs_alias: Set[VariableAlias]
    outputs_alias: Set[VariableAlias]

    def __init__(self, name: str = "composed"):
        super(Compose, self).__init__(name)
        self.inputs_alias = set()
        self.outputs_alias = set()

    @classmethod
    def compose_ops(cls, name: str, ops: Iterable[Operator]):
        composite = Compose(name)

        inputs_or_hiddens: Set[Variable] = set()
        outputs_or_hiddens: Set[Variable] = set()

        for op in ops:
            inputs_or_hiddens.update(op.inputs.values())
            outputs_or_hiddens.update(op.outputs.values())

        inputs: Set[Variable] = inputs_or_hiddens.difference(outputs_or_hiddens)
        outputs: Set[Variable] = outputs_or_hiddens.difference(inputs_or_hiddens)

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

        # FIXME: これは正しいのか?
        for op in ops:
            composite.attributes.update(op.attributes)

        return composite

    @classmethod
    def compose_with_vars(cls, name: str, inputs: Iterable[Variable], outputs: Iterable[Variable]) -> "Compose":
        # グラフを辿って必要なopsを全て取ってくる
        inputs = set(inputs)
        var_queue: List[Variable] = list(outputs)
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
