"""
Descriptor Generator for WebGPU

- kernel source generation
- schedule memory allocation
"""
import os
import os.path as path
import subprocess
import tempfile as tmp

from webdnn.backend.code_generator.allocator import Allocator
from webdnn.backend.interface.descriptor_generator import DescriptorGenerator
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.backend.webgpu.graph_descriptor import GraphDescriptor
from webdnn.backend.webgpu.kernel import Kernel
from webdnn.backend.webgpu.kernels.average_pooling_2d import average_pooling_2d
from webdnn.backend.webgpu.kernels.axiswise_bias import axiswise_bias
from webdnn.backend.webgpu.kernels.axiswise_scale import axiswise_scale
from webdnn.backend.webgpu.kernels.col2im import col2im
from webdnn.backend.webgpu.kernels.concat import concat
from webdnn.backend.webgpu.kernels.elementwise_sum import elementwise_sum
from webdnn.backend.webgpu.kernels.elu import elu
from webdnn.backend.webgpu.kernels.embedding import embedding
from webdnn.backend.webgpu.kernels.flatten import flatten
from webdnn.backend.webgpu.kernels.im2col import im2col
from webdnn.backend.webgpu.kernels.local_response_normalization import local_response_normalization
from webdnn.backend.webgpu.kernels.lstm import lstm
from webdnn.backend.webgpu.kernels.max_pooling_2d import max_pooling_2d
from webdnn.backend.webgpu.kernels.relu import relu
from webdnn.backend.webgpu.kernels.scalar_affine import scalar_affine
from webdnn.backend.webgpu.kernels.sgemm import sgemm
from webdnn.backend.webgpu.kernels.sigmoid import sigmoid
from webdnn.backend.webgpu.kernels.tanh import tanh
from webdnn.backend.webgpu.operators.col2im import Col2Im
from webdnn.backend.webgpu.operators.im2col import Im2Col
from webdnn.backend.webgpu.operators.sgemm import Sgemm
from webdnn.backend.webgpu.optimize_rules.webgpu_optimize_rule import WebGPUOptimizeRule
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.embedding import Embedding
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.operators.tanh import Tanh
from webdnn.util import flags, console
from webdnn.util.json import json


class GraphExecutionData(IGraphExecutionData[Kernel]):
    descriptor: GraphDescriptor

    def __init__(self, descriptor: GraphDescriptor, constants: bytes):
        self.descriptor = descriptor
        self.constants = constants
        self.backend_suffix = "webgpu"

    def save(self, dirname: str):
        os.makedirs(dirname, exist_ok=True)

        with open(path.join(dirname, "graph_{}.json".format(self.backend_suffix)), "w") as f:
            json.dump(self.descriptor, f, indent=2)

        with open(path.join(dirname, "kernels_{}.metal".format(self.backend_suffix)), "w") as f:
            f.write(self.descriptor.concat_kernel_sources())

        with open(path.join(dirname, "weight_{}.bin".format(self.backend_suffix)), "wb") as f:
            f.write(self.constants)


def validate_kernel_source(descriptor: GraphDescriptor):
    # FIXME: WebGPU supports multi shader languages, but this test supposes the language as METAL.

    source = descriptor.concat_kernel_sources()

    with tmp.TemporaryDirectory() as tmpdir:
        source_path = path.join(tmpdir, "kernel.metal")
        lib_path = path.join(tmpdir, "kernel.air")

        with open(source_path, "w+") as f:
            f.write(source)

        with open(os.devnull, "w") as f:
            result = subprocess.run(["type", "xcrun"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                console.warning(
                    "[WebGPUDescriptorGenerator] 'xcrun' command is not found. validation of generated source code in webgpu backend is "
                    "skipped.")
                return

        with open(os.devnull, "w") as f:
            result = subprocess.run(["xcrun", "-sdk", "macosx", "metal", source_path, "-o", lib_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                if result.stderr == b"":
                    console.debug("[WebGPUDescriptorGenerator] Generated kernel source is valid.")

                else:
                    console.warning("[WebGPUDescriptorGenerator] In validating kernel source, warnings are generated.")
                    console.stderr(result.stderr.decode("utf-8"))

            else:
                console.error("[WebGPUDescriptorGenerator] Generated kernel source is invalid.")
                console.stderr(result.stderr.decode("utf-8"))
                exit(result.returncode)


class WebGPUDescriptorGenerator(DescriptorGenerator[Kernel, GraphExecutionData]):
    @classmethod
    def generate(cls, graph: Graph, constant_encoder_name: str = None):
        graph, _ = WebGPUOptimizeRule().optimize(graph)
        if flags.DEBUG:
            traverse.dump(graph)

        memory_layout = Allocator.allocate(graph)
        console.debug(f"[GraphDescriptorGeneratorWebGPU] memory_layout total size: {memory_layout.total_size * 4}")
        console.debug(f"[GraphDescriptorGeneratorWebGPU] memory_layout static size: {memory_layout.static_size * 4}")
        console.debug(f"[GraphDescriptorGeneratorWebGPU] memory_layout dynamic size: {memory_layout.dynamic_size * 4}")

        constant_encoder = ConstantEncoder.get_encoder(constant_encoder_name)
        constants_bytes = constant_encoder.encode(memory_layout)

        console.debug(f"[GraphDescriptorGeneratorWebGPU] constants encoded size: {len(constants_bytes)}")

        kernels = cls.generate_kernels(graph, memory_layout)

        descriptor = GraphDescriptor(
            kernels=kernels,
            memory_layout=memory_layout,
            inputs=graph.inputs,
            outputs=graph.outputs,
            constants_encoding=constant_encoder.name,
            licenses=graph.licenses
        )

        if flags.optimize.VALIDATE_GENERATED_SOURCE:
            validate_kernel_source(descriptor)

        return GraphExecutionData(descriptor, constants_bytes)


def generate(graph: Graph, constant_encoder_name: str = None):
    return WebGPUDescriptorGenerator.generate(graph, constant_encoder_name)


WebGPUDescriptorGenerator.register_handler(AveragePooling2D)(average_pooling_2d)
WebGPUDescriptorGenerator.register_handler(AxiswiseBias)(axiswise_bias)
WebGPUDescriptorGenerator.register_handler(AxiswiseScale)(axiswise_scale)
WebGPUDescriptorGenerator.register_handler(Col2Im)(col2im)
WebGPUDescriptorGenerator.register_handler(Concat)(concat)
WebGPUDescriptorGenerator.register_handler(ElementwiseSum)(elementwise_sum)
WebGPUDescriptorGenerator.register_handler(Elu)(elu)
WebGPUDescriptorGenerator.register_handler(Embedding)(embedding)
WebGPUDescriptorGenerator.register_handler(Flatten)(flatten)
WebGPUDescriptorGenerator.register_handler(Im2Col)(im2col)
WebGPUDescriptorGenerator.register_handler(LocalResponseNormalization)(local_response_normalization)
WebGPUDescriptorGenerator.register_handler(LSTM)(lstm)
WebGPUDescriptorGenerator.register_handler(MaxPooling2D)(max_pooling_2d)
WebGPUDescriptorGenerator.register_handler(Relu)(relu)
WebGPUDescriptorGenerator.register_handler(ScalarAffine)(scalar_affine)
WebGPUDescriptorGenerator.register_handler(Sgemm)(sgemm)
WebGPUDescriptorGenerator.register_handler(Sigmoid)(sigmoid)
WebGPUDescriptorGenerator.register_handler(Tanh)(tanh)
