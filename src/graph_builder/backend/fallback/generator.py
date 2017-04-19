# -*- coding:utf-8 -*-

"""
Kernel Builder for Fallback (pure js)

- kernel source generation
- schedule memory allocation
"""

from typing import Tuple, List, Set

import numpy as np

from graph_builder.backend.fallback import kernels as K
from graph_builder.backend.fallback.allocator import Allocator, MemoryLayout
from graph_builder.backend.fallback.graph_descriptor import GraphDescriptor
from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.graph import Operator, operators as O
from graph_builder.util import flags


def generate(graph: Operator) -> Tuple[GraphDescriptor, np.array]:
    variables_layout, constants_layout, constants_data = Allocator.allocate(graph)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorWebGPU] constants_layout total size: {constants_data.size} * sizeof(float)")
        print(f"[GraphDescriptorGeneratorWebGPU] variables_layout total size: {variables_layout.size} * sizeof(float)")

    kernels = generate_kernels(graph, constants_layout, variables_layout)

    descriptor = GraphDescriptor(
        kernels=kernels,
        constants_layout=constants_layout,
        variables_layout=variables_layout,
        inputs=graph.inputs,
        outputs=graph.outputs)

    return descriptor, constants_data


def generate_kernels(op: Operator, constants_layout: MemoryLayout, variables_layout: MemoryLayout) -> List[Kernel]:
    if isinstance(op, O.Compose):
        kernels = generate_kernel_compose(op, constants_layout, variables_layout)

    elif isinstance(op, O.Linear):
        kernels = K.linear(op)

    elif isinstance(op, O.AxiswiseBias):
        kernels = K.axiswise_bias(op)

    elif isinstance(op, O.Convolution2D):
        kernels = K.convolution_2d(op)

    elif isinstance(op, O.Relu):
        kernels = K.relu(op)

    else:
        raise NotImplementedError(f"{op} is Unknown for Fallback Descriptor Generator")

    return kernels


def generate_kernel_compose(op: O.Compose, constants_layout: MemoryLayout, variables_layout: MemoryLayout) -> List[Kernel]:
    kernels: List[Kernel] = []
    op_queue: List[Operator] = []
    op_checked: Set[Operator] = set()

    for var in op.outputs_alias:
        op_queue.append(var.output_from)

    while len(op_queue) > 0:
        op = op_queue.pop(0)
        if op in op_checked:
            continue
        op_checked.add(op)

        sub_kernels = generate_kernels(op, constants_layout, variables_layout)
        kernels = sub_kernels + kernels
        for v in op.inputs.values():
            if v.output_from is not None:
                op_queue.append(v.output_from)

    return kernels
