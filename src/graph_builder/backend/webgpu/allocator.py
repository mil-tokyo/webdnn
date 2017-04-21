from typing import Dict, Tuple, List, Set

import numpy as np

from graph_builder.graph import operators as O
from graph_builder.graph.graph import Variable, Operator
from graph_builder.graph.operators.compose import VariableAlias
from graph_builder.graph.operators import attributes as A
from graph_builder.graph.variables import Constant, attributes as VA
from graph_builder.optimizer import util
from graph_builder.util import json


class Allocation(json.SerializableMixin):
    variable: Variable
    offset: int

    def __init__(self,
                 variable: Variable,
                 offset: int):
        self.variable = variable
        self.offset = offset

    @property
    def size(self) -> int:
        return self.variable.size

    def _to_serializable_(self):
        return {
            "name": self.variable.name,
            "offset": self.offset,
            "size": self.size
        }


class MemoryLayout(json.SerializableMixin):
    size: int
    __dict__: Dict[str, Allocation]

    def __init__(self):
        self.__dict__ = {}

    def _to_serializable_(self):
        return {
            "total_size": self.size,
            "allocation": {a.variable.name: a for _, a in self.__dict__.items()}
        }

    def __getitem__(self, var: Variable):
        return self.__dict__[var.name]

    def __contains__(self, var: Variable):
        return var.name in self.__dict__

    def append(self, var: Variable, offset: int = -1):
        if offset == -1:
            offset = self.size

        if isinstance(var, VariableAlias):
            var = var.original

        self.__dict__[var.name] = Allocation(var, offset)

    @property
    def size(self) -> int:
        size = 0
        for _, a in self.__dict__.items():
            size = max(a.offset + a.size, size)

        return size


class Allocator:
    layout: MemoryLayout

    @classmethod
    def allocate(cls, graph: Operator) -> Tuple[MemoryLayout, MemoryLayout, np.array]:
        variables = util.listup_variables(graph, remove_alias=True)
        for i, v in enumerate(variables):
            v.name = f"v{i}"

        constants = set(util.filter_nodes(variables, VA.Constant))  # type: Set[Constant]
        variables = variables.difference(constants)

        variables = list(variables)
        constants = list(constants)

        constants_layout, data = cls.allocate_constants(constants)
        variables_layout = cls.allocate_variables(graph, variables)
        return variables_layout, constants_layout, data

    @classmethod
    def allocate_constants(cls, constants: List[Constant]) -> Tuple[MemoryLayout, np.ndarray]:
        layout = MemoryLayout()

        for constant in constants:
            if constant in layout:
                continue

            layout.append(constant)

        buffer = np.zeros(layout.size, dtype=np.float32)
        for constant in constants:
            allocation = layout[constant]
            buffer[allocation.offset:allocation.offset + allocation.size] = constant.data.flatten()

        return layout, buffer

    @classmethod
    def allocate_variables(cls, graph: Operator, variables: List[Variable]) -> MemoryLayout:
        layout = MemoryLayout()

        ops = util.listup_operator_in_order(graph)

        # 計算グラフを辿りながら、retain回数をカウントし、ゼロになったら解放する
        retain_count: Dict[Variable, int] = {v: 0 for v in variables}
        free_list: List[Tuple(int, int)] = []  # [(offset, size)]

        for var in graph.inputs.values():
            if isinstance(var, VariableAlias):
                var = var.original

            if isinstance(var, Constant):
                continue

            layout.append(var)

        for op in ops:
            for var in op.outputs.values():
                if isinstance(var, VariableAlias):
                    var = var.original

                if isinstance(var, Constant):
                    continue

                if var not in layout:
                    # 新しく割り当てる

                    # FIXME:
                    # X --[Reshape]--> Y --[ReLU]--> Z
                    # |
                    # +---[Op]--> W
                    #
                    # 上のような状況だと、YはXと同じメモリを使うことになる
                    # ReLUはInplace指定なため、Yの入力先が自分(ReLU)だけであることを確認した上で、ZをYと同じ位置(=Xと同じ位置)に確保しようとするが
                    # こうするとOpの演算結果Wがおかしくなる
                    #
                    # flag_inplace = util.check_attribute_match(op, A.Inplace) and len(list(op.inputs.values())[0].input_to) == 1
                    # if isinstance(op, O.Reshape) or flag_inplace:

                    if isinstance(op, O.Reshape):
                        # 入力のメモリをそのまま使う
                        var_in = list(op.inputs.values())[0]
                        layout.append(var, layout[var_in].offset)
                        retain_count[var] = len(var.input_to)
                        retain_count[var_in] += 1

                    else:
                        size = var.size
                        spaces = sorted([space for space in free_list if space[1] >= size], key=lambda x: x[1])
                        if len(spaces) > 0:
                            # 十分なスペースがあった
                            space = spaces[0]
                            free_list.remove(space)
                            layout.append(var, offset=space[0])
                            if space[1] > var.size:
                                free_list.append((space[0] + var.size, space[1] - var.size))

                        else:
                            # 十分なスペースが無かった
                            layout.append(var)
                            retain_count[var] = len(var.input_to)

            for var in op.inputs.values():
                if isinstance(var, VariableAlias):
                    var = var.original

                if isinstance(var, Constant):
                    continue

                retain_count[var] -= 1
                if retain_count[var] == 0:
                    allocation = layout[var]
                    free_list.append((allocation.offset, allocation.size))
                    # TODO: Defragmentation

        return layout
