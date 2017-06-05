# -*- coding:utf-8 -*-

"""
Kernel Builder for Fallback (pure js)

- kernel source generation
- schedule memory allocation
"""
import os
import os.path as path
from typing import List

from webdnn.backend.code_generator.allocator import Allocator
from webdnn.backend.fallback.graph_descriptor import GraphDescriptor
from webdnn.backend.fallback.kernel import Kernel
from webdnn.backend.fallback.kernels.average_pooling_2d import average_pooling_2d
from webdnn.backend.fallback.kernels.axiswise_bias import axiswise_bias
from webdnn.backend.fallback.kernels.axiswise_scale import axiswise_scale
from webdnn.backend.fallback.kernels.concat import concat
from webdnn.backend.fallback.kernels.convolution_2d import convolution_2d
from webdnn.backend.fallback.kernels.elementwise_sum import elementwise_sum
from webdnn.backend.fallback.kernels.flatten import flatten
from webdnn.backend.fallback.kernels.linear import linear
from webdnn.backend.fallback.kernels.local_response_normalization import local_response_normalization
from webdnn.backend.fallback.kernels.max_pooling_2d import max_pooling_2d
from webdnn.backend.fallback.kernels.relu import relu
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.util import flags
from webdnn.util.json import json


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
    memory_layout = Allocator.allocate(graph)
    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorFallback] memory_layout total size: {memory_layout.size * 4}")

    constant_encoder = ConstantEncoder.get_encoder(constant_encoder_name)
    constants_bytes = constant_encoder.encode(memory_layout)

    if flags.DEBUG:
        print(f"[GraphDescriptorGeneratorFallback] constants encoded size: {len(constants_bytes)}")

    descriptor = GraphDescriptor(
        kernels=generate_kernels(graph),
        memory_layout=memory_layout,
        inputs=graph.inputs,
        outputs=graph.outputs,
        constants_encoding=constant_encoder.name,
        licenses=graph.licenses)

    return GraphExecutionData(descriptor, constants_bytes)


# noinspection PyUnusedLocal
def generate_kernels(graph: Graph) -> List[Kernel]:
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

        elif isinstance(op, Concat):
            kernels += concat(op)

        elif isinstance(op, LocalResponseNormalization):
            kernels += local_response_normalization(op)

        else:
            raise NotImplementedError(f"{op} is Unknown for Fallback Descriptor Generator")

    return kernels
