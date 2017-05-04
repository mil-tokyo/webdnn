from typing import Dict, Tuple, List, Set

import numpy as np

from graph_builder.backend.interface.memory_layout import IMemoryLayout, IAllocation
from graph_builder.graph.graph import Graph
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.optimize_rule import util
from graph_builder.util import json, flags


class AllocationAnalysisData:
    variable: Variable
    start: int
    end: int
    offset: int

    def __init__(self, variable, start, end=-1, offset=-1):
        self.variable = variable
        self.start = start
        self.end = end
        self.offset = offset

    def is_covered(self, other: "AllocationAnalysisData") -> bool:
        return not (self.start >= other.end or other.start >= self.end)


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
        """
        alloc   V1( 6block )
        alloc   V2( 7block )
        alloc   V3( 7block )
        release V2
        alloc   V4(8block)

        について、確保の方法に寄ってメモリプールサイズが異なる

        alloc   V1 :  <-V1->
        alloc   V2 :  <-V1-><-V2-->
        alloc   V3 :  <-V1-><-V2--><-V3-->
        release V2 :  <-V1->.......<-V3-->
        alloc   V4 :  <-V1->.......<-V3--><-V4--->

        alloc   V1 :  <-V1->
        alloc   V2 :  <-V1->.......<-V2-->
        alloc   V3 :  <-V1-><-V3--><-V2-->
        release V2 :  <-V1-><-V3-->
        alloc   V4 :  <-V1-><-V3--><-V4--->

        alloc   V1 :  ........<-V1->
        alloc   V2 :  <-V2-->.<-V1->
        alloc   V3 :  <-V2-->.<-V1-><-V3-->
        release V2 :  ........<-V1-><-V3-->
        alloc   V4 :  <-V4---><-V1-><-V3-->

        alloc   V1 :  ........<-V1->
        alloc   V2 :  ........<-V1->
        alloc   V3 :  <-V2-->.<-V1-><-V3-->
        release V2 :  ........<-V1-><-V3-->
        alloc   V4 :  <-V4---><-V1-><-V3-->

        最適解は1つとは限らない(その後だれが解放されるのか、による)
        """

        ops = util.listup_operators(graph)
        LIFETIME_FOREVER = len(ops) + 1
        analysis_table: Dict[Variable, AllocationAnalysisData] = {}

        # 計算グラフを辿りながら、retain回数をカウントし、生存期間のテーブルを作成する
        retain_count: Dict[Variable, int] = {v: 0 for v in variables}
        allocated: Set[Variable] = set()

        for var in graph.inputs:
            if isinstance(var, ConstantVariable):
                continue

            analysis_table[var] = AllocationAnalysisData(var, 0, LIFETIME_FOREVER)

        for t, op in enumerate(ops):
            for var in op.outputs.values():
                if isinstance(var, ConstantVariable):
                    continue

                if var not in allocated:
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
                            retain_count[v_in] += len(var.input_to)

                            allocated.add(var)
                            flag_allocated = True

                    if not flag_allocated:
                        # 新しくメモリを確保
                        analysis_table[var] = AllocationAnalysisData(var, t, LIFETIME_FOREVER)
                        retain_count[var] = len(var.input_to)

                        allocated.add(var)
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
                    analysis_table[var].end = t + 1

        # メモリ共有可能判定
        analysis_list = list(sorted(sorted(analysis_table.values(), key=lambda x: x.start), key=lambda x: x.variable.size, reverse=True))
        allocated_items: List[AllocationAnalysisData] = []
        memory_offset_table = {}

        while len(analysis_list) > 0:
            item1 = analysis_list.pop(0)
            combined_items = [item1]

            for item2 in analysis_list:
                flag_combindable = True

                for item3 in combined_items:
                    if item3.is_covered(item2):
                        flag_combindable = False
                        break

                if flag_combindable:
                    combined_items.append(item2)

            for item2 in combined_items:
                offset = 0

                for t in range(item2.start, item2.end):
                    if t in memory_offset_table:
                        offset = max(offset, memory_offset_table[t])

                item2.offset = offset

                for t in range(item2.start, item2.end):
                    memory_offset_table[t] = offset + item2.variable.size

            for item2 in combined_items[1:]:
                analysis_list.remove(item2)

            allocated_items += combined_items

        # メモリ配置の確定
        allocation_dict = {item.variable: item.offset for item in allocated_items}
        layout = MemoryLayout()
        for var in variables:
            original_var = var
            while "inplace_src" in var.parameters:
                var = var.parameters["inplace_src"]

            layout.append(original_var, allocation_dict[var])

        if flags.DEBUG and flags.backend.webgpu.VISUALIZE_MEMORY_ALLOCATION:
            visualize_allocation(layout.size, allocated_items, variables, ops)

        return layout


def visualize_allocation(total_size: int, allocated_items: List[AllocationAnalysisData], variables: List[Variable], ops: List[Operator]):
    UNIT_HEIGHT = 14

    class RenderingInfo:
        names: List[str]
        data: AllocationAnalysisData

        def __init__(self, data: AllocationAnalysisData):
            self.names = []
            self.data = data

        @property
        def offset(self):
            return self.data.offset

        @property
        def size(self):
            return self.data.variable.size

        @property
        def top(self):
            return f"{self.data.start * UNIT_HEIGHT}px"

        @property
        def height(self):
            return f"{(self.data.end - self.data.start) * UNIT_HEIGHT + 1}px"

        @property
        def left(self):
            return f"{self.offset * 100 / total_size}%"

        @property
        def width(self):
            return f"calc({self.size * 100 / total_size}% + 1px)"

        def generate_html(self):
            return f"""<div class="Allocation" style="top: {self.top}; height: {self.height}; left: {self.left}; width: {self.width}" """ \
                   + f"""title="{", ".join(self.names)}
size: {self.size}
offset: {self.offset}
lifetime: {self.data.start} - {self.data.end} 
">
    <p>{", ".join(self.names)}</p>
</div>"""

    allocation_dict = {item.variable: item for item in allocated_items}
    rendering_dict: Dict[Variable, RenderingInfo] = {}

    html = """<html>
<head>
    <style>
        html, body {
            width: 100%;
            height: 200%;
            margin: 0;
            font-size: 8px;
        }

        body {
            padding: 32px;
            box-sizing: border-box;
        }
        
        .MemoryLayout {
            position: relative;
            background: #888;
        }
        
        .Allocation {
            position: absolute;
            border: 1px solid #000;
            display: block;
            padding: 8px;
            box-sizing: border-box;
            overflow: hidden;
            background: #0f0;
        }
        
        p {
            margin: 0;
            white-space: nowrap;
        }
    </style>
</head>
<body>
<header style="margin-bottom: 32px;">
    <h1>Memory Allocation Visualization</h1>
    <p>縦軸：時間経過（上から下へ）</p>
    <p>横軸：メモリアドレス</p>
    <p>各要素はカーソルホバーで詳細が見られます。</p>
</header>
    <div class="MemoryLayout" style="height: """ + str(UNIT_HEIGHT * (len(ops) + 1) + 1) + """px;">
"""

    for variable in variables:
        original_var = variable
        while "inplace_src" in variable.parameters:
            variable = variable.parameters["inplace_src"]

        if variable not in rendering_dict:
            rendering_dict[variable] = RenderingInfo(allocation_dict[variable])

        rendering_dict[variable].names.append(original_var.name)

    for item in rendering_dict.values():
        html += item.generate_html()

    html += """
    </div>
</body>
</html>
"""

    with open('memory_visualize.html', "w+") as f:
        f.write(html)
