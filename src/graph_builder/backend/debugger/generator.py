import os.path as path
import subprocess
import tempfile as tmp
from typing import Tuple, List, Set

import numpy as np

from graph_builder.backend.webgpu import kernels as K
from graph_builder.backend.webgpu.allocator import Allocator, MemoryLayout
from graph_builder.backend.webgpu.graph_descriptor import GraphDescriptor
from graph_builder.backend.webgpu.kernel import Kernel
from graph_builder.graph import Operator, operators as O
from graph_builder.optimizer import util
from graph_builder.util import flags


header = """
<html>
<head>
    <meta charset=>
"""

fotter = """
"""
def generate(graph: Operator) -> GraphDescriptor:
    html = header
    for op in util.listup_operator_in_order(graph):
        html += f"""
<
"""
    pass
