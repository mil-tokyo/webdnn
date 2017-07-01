# -*- coding:utf-8 -*-

"""
Kernel Builder for Fallback (pure js)

- kernel source generation
- schedule memory allocation
"""
import os
import os.path as path

from webdnn.backend.code_generator.allocator import Allocator
from webdnn.backend.fallback.graph_descriptor import GraphDescriptor
from webdnn.backend.fallback.kernel import Kernel
from webdnn.backend.fallback.kernels.average_pooling_2d import average_pooling_2d
from webdnn.backend.fallback.kernels.axiswise_bias import axiswise_bias
from webdnn.backend.fallback.kernels.axiswise_scale import axiswise_scale
from webdnn.backend.fallback.kernels.clipped_relu import clipped_relu
from webdnn.backend.fallback.kernels.concat import concat
from webdnn.backend.fallback.kernels.convolution_2d import convolution_2d
from webdnn.backend.fallback.kernels.elementwise_sum import elementwise_sum
from webdnn.backend.fallback.kernels.elu import elu
from webdnn.backend.fallback.kernels.flatten import flatten
from webdnn.backend.fallback.kernels.hard_sigmoid import hard_sigmoid
from webdnn.backend.fallback.kernels.leaky_relu import leaky_relu
from webdnn.backend.fallback.kernels.linear import linear
from webdnn.backend.fallback.kernels.local_response_normalization import local_response_normalization
from webdnn.backend.fallback.kernels.max_pooling_2d import max_pooling_2d
from webdnn.backend.fallback.kernels.reinterpret_axis import reinterpret_axis
from webdnn.backend.fallback.kernels.relu import relu
from webdnn.backend.fallback.kernels.reshape import reshape
from webdnn.backend.fallback.kernels.scalar_affine import scalar_affine
from webdnn.backend.fallback.kernels.sigmoid import sigmoid
from webdnn.backend.fallback.kernels.softmax import softmax
from webdnn.backend.fallback.kernels.softplus import softplus
from webdnn.backend.fallback.kernels.softsign import softsign
from webdnn.backend.fallback.kernels.tanh import tanh
from webdnn.backend.interface.generator import DescriptorGenerator
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.clipped_relu import ClippedRelu
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.hard_sigmoid import HardSigmoid
from webdnn.graph.operators.leaky_relu import LeakyRelu
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.reinterpret_axis import ReinterpretAxis
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.softmax import Softmax
from webdnn.graph.operators.softplus import Softplus
from webdnn.graph.operators.softsign import Softsign
from webdnn.graph.operators.tanh import Tanh
from webdnn.util import console
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

        with open(path.join(dirname, "kernels_{}.js".format(self.backend_suffix)), "w") as f:
            f.write(self.descriptor.concat_kernel_sources())

        with open(path.join(dirname, "weight_{}.bin".format(self.backend_suffix)), "wb") as f:
            f.write(self.constants)


class FallbackDescriptorGenerator(DescriptorGenerator[Kernel, GraphExecutionData]):
    @classmethod
    def generate(cls, graph: Graph, **kwargs):
        memory_layout = Allocator.allocate(graph)

        console.debug(f"[FallbackDescriptorGenerator] memory_layout total size: {memory_layout.total_size * 4}")
        console.debug(f"[FallbackDescriptorGenerator] memory_layout static size: {memory_layout.static_size * 4}")
        console.debug(f"[FallbackDescriptorGenerator] memory_layout dynamic size: {memory_layout.dynamic_size * 4}")

        constant_encoder = ConstantEncoder.get_encoder(kwargs.get("constant_encoder_name", None))
        constants_bytes = constant_encoder.encode(memory_layout)

        console.debug(f"[FallbackDescriptorGenerator] constants encoded size: {len(constants_bytes)}")

        descriptor = GraphDescriptor(
            kernels=cls.generate_kernels(graph, memory_layout),
            memory_layout=memory_layout,
            inputs=graph.inputs,
            outputs=graph.outputs,
            constants_encoding=constant_encoder.name,
            licenses=graph.licenses)

        return GraphExecutionData(descriptor, constants_bytes)


def generate(graph: Graph, **kwargs):
    return FallbackDescriptorGenerator.generate(graph, **kwargs)


FallbackDescriptorGenerator.register_handler(AveragePooling2D)(average_pooling_2d)
FallbackDescriptorGenerator.register_handler(AxiswiseBias)(axiswise_bias)
FallbackDescriptorGenerator.register_handler(AxiswiseScale)(axiswise_scale)
FallbackDescriptorGenerator.register_handler(Concat)(concat)
FallbackDescriptorGenerator.register_handler(ClippedRelu)(clipped_relu)
FallbackDescriptorGenerator.register_handler(Convolution2D)(convolution_2d)
FallbackDescriptorGenerator.register_handler(ElementwiseSum)(elementwise_sum)
FallbackDescriptorGenerator.register_handler(Elu)(elu)
FallbackDescriptorGenerator.register_handler(Flatten)(flatten)
FallbackDescriptorGenerator.register_handler(HardSigmoid)(hard_sigmoid)
FallbackDescriptorGenerator.register_handler(LeakyRelu)(leaky_relu)
FallbackDescriptorGenerator.register_handler(Linear)(linear)
FallbackDescriptorGenerator.register_handler(LocalResponseNormalization)(local_response_normalization)
FallbackDescriptorGenerator.register_handler(MaxPooling2D)(max_pooling_2d)
FallbackDescriptorGenerator.register_handler(ScalarAffine)(scalar_affine)
FallbackDescriptorGenerator.register_handler(Sigmoid)(sigmoid)
FallbackDescriptorGenerator.register_handler(Softmax)(softmax)
FallbackDescriptorGenerator.register_handler(Softplus)(softplus)
FallbackDescriptorGenerator.register_handler(Softsign)(softsign)
FallbackDescriptorGenerator.register_handler(ReinterpretAxis)(reinterpret_axis)
FallbackDescriptorGenerator.register_handler(Relu)(relu)
FallbackDescriptorGenerator.register_handler(Reshape)(reshape)
FallbackDescriptorGenerator.register_handler(Tanh)(tanh)
