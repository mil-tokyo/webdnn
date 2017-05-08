# -*- coding:utf-8 -*-

"""
Kernel Builder for Fallback (pure js)

- kernel source generation
- schedule memory allocation
"""
import os
import os.path as path
from typing import List

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
from graph_builder.backend.fallback.kernels.local_response_normalization import local_response_normalization
from graph_builder.backend.fallback.kernels.max_pooling_2d import max_pooling_2d
from graph_builder.backend.fallback.kernels.relu import relu
from graph_builder.backend.interface.graph_descriptor import IGraphExecutionData
from graph_builder.encoder.constant_encoder import ConstantEncoder
from graph_builder.graph import traverse
from graph_builder.graph.graph import Graph
from graph_builder.graph.operators.average_pooling_2d import AveragePooling2D
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.operators.elementwise_sum import ElementwiseSum
from graph_builder.graph.operators.flatten import Flatten
from graph_builder.graph.operators.linear import Linear
from graph_builder.graph.operators.local_response_normalization import LocalResponseNormalization
from graph_builder.graph.operators.max_pooling_2d import MaxPooling2D
from graph_builder.graph.operators.relu import Relu
from graph_builder.util import flags
from graph_builder.util.json import json


class GraphExecutionData(IGraphExecutionData):
    descriptor: GraphDescriptor

    def __init__(self, descriptor: GraphDescriptor, constants: bytes):
        self.descriptor = descriptor
        self.constants = constants
        self.backend_suffix = "fallback"

    def save(self, dirname: str):
        os.makedirs(dirname, exist_ok=True)
        
        with open(path.join(dirname, "graph_{}.json".format(self.backend_suffix)), "w") as f:
            json.dump(self.descriptor, f, indent=2)

        with open(path.join(dirname, "weight_{}.bin".format(self.backend_suffix)), "wb") as f:
            f.write(self.constants)


def generate(graph: Graph, constant_encoder_name: str = None) -> GraphExecutionData:
    variables_layout, constants_layout, constants_data = Allocator.allocate(graph)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorFallback] constants_layout total size: {constants_data.size} * sizeof(float)")
        print(
            f"[GraphDescriptorGeneratorFallback] variables_layout total size: {variables_layout.size} * sizeof(float)")
    constant_encoder = ConstantEncoder.get_encoder(constant_encoder_name)
    constants_bytes = constant_encoder.encode(constants_layout, constants_data)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorFallback] constants encoded size: {len(constants_bytes)}")

    kernels = generate_kernels(graph, constants_layout, variables_layout)

    descriptor = GraphDescriptor(
        kernels=kernels,
        constants_layout=constants_layout,
        variables_layout=variables_layout,
        inputs=graph.inputs,
        outputs=graph.outputs,
        constants_encoding=constant_encoder.name)

    return GraphExecutionData(descriptor, constants_bytes)


# noinspection PyUnusedLocal
def generate_kernels(graph: Graph, constants_layout: MemoryLayout, variables_layout: MemoryLayout) -> List[Kernel]:
    kernels: List[Kernel] = []
    for op in traverse.listup_operators(graph):
        if isinstance(op, Linear):
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

        elif isinstance(op, LocalResponseNormalization):
            kernels += local_response_normalization(op)

        else:
            raise NotImplementedError(f"{op} is Unknown for Fallback Descriptor Generator")

    return kernels
