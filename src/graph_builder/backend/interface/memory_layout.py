from typing import Dict, Tuple, List, Set

import numpy as np

from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.attributes.inplace import Inplace
from graph_builder.graph.variable import Variable
from graph_builder.graph.variables.attributes.constant import Constant
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.optimize_rule import util
from graph_builder.util import json, flags


class IAllocation:
    variable: Variable
    offset: int

    @property
    def size(self) -> int:
        raise NotImplementedError()


class IMemoryLayout:
    size: int
    __dict__: Dict[str, IAllocation]

    @property
    def size(self) -> int:
        raise NotImplementedError()
