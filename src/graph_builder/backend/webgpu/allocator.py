from typing import Dict, Tuple, List, Set

import numpy as np

from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.backend.interface.memory_layout import IMemoryLayout, IAllocation
from graph_builder.optimize_rule import util
from graph_builder.util import json, flags


class Allocation(json.SerializableMixin, IAllocation):
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


class MemoryLayout(json.SerializableMixin, IMemoryLayout):
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
    def allocate(cls, graph: Graph) -> Tuple[MemoryLayout, MemoryLayout, np.array]:
        variables = set(util.listup_variables(graph))
        for i, v in enumerate(variables):
            v.name = f"v{i}"

        constants = set(util.filter_nodes(variables, Constant))  # type: Set[ConstantVariable]
        variables = variables.difference(constants)

        variables = list(variables)
        constants = list(constants)

        constants_layout, data = cls.allocate_constants(constants)
        variables_layout = cls.allocate_variables(graph, variables)
        return variables_layout, constants_layout, data

    @classmethod
    def allocate_constants(cls, constants: List[ConstantVariable]) -> Tuple[MemoryLayout, np.ndarray]:
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
    def allocate_variables(cls, graph: Graph, variables: List[Variable]) -> MemoryLayout:
        layout = MemoryLayout()

        # 計算グラフを辿りながら、retain回数をカウントし、ゼロになったら解放する
        retain_count: Dict[Variable, int] = {v: 0 for v in variables}
        free_list: List[Tuple(int, int)] = []  # [(offset, size)]

        for var in graph.inputs:
            if isinstance(var, ConstantVariable):
                continue

            layout.append(var)

        for op in util.listup_operators(graph):
            for var in op.outputs.values():
                if isinstance(var, ConstantVariable):
                    continue

                if var not in layout:
                    # 新規に確保する
                    flag_allocated = False

                    if not flag_allocated and util.check_attribute_match(op, Inplace):
                        # Inplace処理

                        input_variables = util.filter_nodes(op.inputs.values(), Constant, mode_not=True)
                        if len(input_variables) > 1:
                            if flags.DEBUG:
                                print(f"[WebGPUAllocator] Inplace operator with ambiguous memory location is detected. "
                                      + f"Allocator skipped inplace allocation and allocate other memory. "
                                      + f"Operator: {op}")

                        else:
                            # 入力のメモリをそのまま使う
                            v_in = input_variables[0]
                            while "inplace_src" in v_in.parameters:
                                v_in = v_in.parameters["inplace_src"]
                            var.parameters["inplace_src"] = v_in

                            layout.append(var, layout[v_in].offset)
                            retain_count[v_in] += len(var.input_to)
                            flag_allocated = True

                    if not flag_allocated:
                        # 新しくメモリを確保

                        size = var.size
                        spaces = sorted([space for space in free_list if space[1] >= size], key=lambda x: x[1])
                        retain_count[var] = len(var.input_to)

                        if len(spaces) > 0:
                            # 十分なスペースがあった
                            space = spaces[0]
                            free_list.remove(space)
                            layout.append(var, offset=space[0])
                            if space[1] > var.size:
                                free_list.append((space[0] + var.size, space[1] - var.size))
                            flag_allocated = True

                        else:
                            # 十分なスペースが無かった
                            layout.append(var)
                            flag_allocated = True

                    if not flag_allocated:
                        raise ValueError("[WebGPUAllocator] Memory Allocation Failed.")

            for var in op.inputs.values():
                if isinstance(var, ConstantVariable):
                    continue

                while "inplace_src" in var.parameters:
                    var = var.parameters["inplace_src"]
                retain_count[var] -= 1

                if retain_count[var] == 0:
                    # 解放
                    allocation = layout[var]
                    space1 = (allocation.offset, allocation.size)
                    free_list.append(space1)

                    # 解放済み領域の結合(デフラグ)
                    flag_changed = True
                    while flag_changed:
                        flag_changed = False
                        for space2 in list(free_list):

                            if space2[0] + space2[1] == space1[0]:
                                free_list.remove(space1)
                                free_list.remove(space2)
                                space1 = (space2[0], space2[1] + space1[1])
                                free_list.append(space1)
                                flag_changed = True

                            if space2[0] == space1[0] + space1[1]:
                                free_list.remove(space1)
                                free_list.remove(space2)
                                space1 = (space1[0], space2[1] + space1[1])
                                free_list.append(space1)
                                flag_changed = True

        return layout
