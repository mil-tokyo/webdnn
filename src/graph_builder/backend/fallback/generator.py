# -*- coding:utf-8 -*-

"""
Kernel Builder for Fallback (pure js)

- kernel source generation
- schedule memory allocation
"""

from typing import Tuple, List

import numpy as np

from graph_builder.backend.fallback.allocator import Allocator, MemoryLayout
from graph_builder.backend.fallback.graph_descriptor import GraphDescriptor
from graph_builder.backend.fallback.kernel import Kernel
from graph_builder.backend.fallback.kernels.average_pooling_2d import average_pooling_2d
from graph_builder.backend.fallback.kernels.axiswise_bias import axiswise_bias
from graph_builder.backend.fallback.kernels.axiswise_scale import axiswise_scale
from graph_builder.backend.fallback.kernels.convolution_2d import convolution_2d
from graph_builder.backend.fallback.kernels.elementwise_sum import elementwise_sum
from graph_builder.backend.fallback.kernels.flatten import flatten
from graph_builder.backend.fallback.kernels.linear import linear
from graph_builder.backend.fallback.kernels.max_pooling_2d import max_pooling_2d
from graph_builder.backend.fallback.kernels.relu import relu
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.average_pooling_2d import AveragePooling2D
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.operators.compose import Compose
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.operators.elementwise_sum import ElementwiseSum
from graph_builder.graph.operators.flatten import Flatten
from graph_builder.graph.operators.linear import Linear
from graph_builder.graph.operators.max_pooling_2d import MaxPooling2D
from graph_builder.graph.operators.relu import Relu
from graph_builder.optimize_rule import util
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


# noinspection PyUnusedLocal
def generate_kernels(graph: Operator, constants_layout: MemoryLayout, variables_layout: MemoryLayout) -> List[Kernel]:
    kernels: List[Kernel] = []
    for op in util.listup_operators(graph):
        if isinstance(op, Compose):
            # kernels = generate_kernel_compose(op, constants_layout, variables_layout)
            continue

        elif isinstance(op, Linear):
            kernels += linear(op)

        elif isinstance(op, AxiswiseBias):
            kernels += axiswise_bias(op)

        elif isinstance(op, AxiswiseScale):
            kernels += axiswise_scale(op)

        elif isinstance(op, Convolution2D):
            kernels += convolution_2d(op)

        elif isinstance(op, MaxPooling2D):
            kernels += max_pooling_2d(op)

        elif isinstance(op, AveragePooling2D):
            kernels += average_pooling_2d(op)

        elif isinstance(op, ElementwiseSum):
            kernels += elementwise_sum(op)

        elif isinstance(op, Flatten):
            kernels += flatten(op)

        elif isinstance(op, Relu):
            kernels += relu(op)

        else:
            raise NotImplementedError(f"{op} is Unknown for Fallback Descriptor Generator")

    return kernels
