import os
import os.path as path
import subprocess
import tempfile as tmp

from webdnn.backend.code_generator.allocator import allocate
from webdnn.backend.interface.generator import DescriptorGenerator
from webdnn.backend.interface.graph_descriptor import IGraphExecutionData
from webdnn.backend.webgpu.graph_descriptor import GraphDescriptor
from webdnn.backend.webgpu.kernel import Kernel
from webdnn.backend.webgpu.optimize_rules.webgpu_optimize_rule import WebGPUOptimizeRule
from webdnn.encoder.constant_encoder import ConstantEncoder
from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.util import flags, console
from webdnn.util import json


class GraphExecutionData(IGraphExecutionData[Kernel]):
    descriptor: GraphDescriptor

    def __init__(self, graph: Graph, descriptor: GraphDescriptor, constants: bytes):
        self.graph = graph
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

    if os.name != 'posix':
        # os.name in mac is 'posix', and xcrun command is only in mac
        console.warning(
            "[WebGPUDescriptorGenerator] 'xcrun' command is not found. validation of generated source code in webgpu backend is "
            "skipped.")
        return

    with tmp.TemporaryDirectory() as tmpdir:
        source_path = path.join(tmpdir, "kernel.metal")
        lib_path = path.join(tmpdir, "kernel.air")

        with open(source_path, "w+") as f:
            f.write(source)

        try:
            result = subprocess.run(["xcrun", "-sdk", "macosx", "metal", source_path, "-o", lib_path],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                if result.stderr == b"":
                    console.debug("[WebGPUDescriptorGenerator] Generated kernel source is valid.")

                else:
                    console.warning(
                        "[WebGPUDescriptorGenerator] In validating kernel source, warnings are generated.")
                    console.stderr(result.stderr.decode("utf-8"))

            else:
                console.error("[WebGPUDescriptorGenerator] Generated kernel source is invalid.")
                console.stderr(result.stderr.decode("utf-8"))
                exit(result.returncode)

        except FileNotFoundError:
            console.warning(
                "[WebGPUDescriptorGenerator] 'xcrun' command is not found. validation of generated source code in webgpu backend is "
                "skipped.")
            return


class WebGPUDescriptorGenerator(DescriptorGenerator[Kernel, GraphExecutionData]):
    @classmethod
    def generate(cls, graph: Graph, **kwargs):
        graph, _ = WebGPUOptimizeRule().optimize(graph)
        if flags.DEBUG:
            traverse.dump(graph)

        memory_layout = allocate(graph)
        console.debug(f"[WebGPUDescriptorGenerator] memory_layout total size: {memory_layout.total_size * 4}[B]")
        console.debug(f"[WebGPUDescriptorGenerator] memory_layout static size: {memory_layout.static_size * 4}[B]")
        console.debug(f"[WebGPUDescriptorGenerator] memory_layout dynamic size: {memory_layout.dynamic_size * 4}[B]")

        constant_encoder = ConstantEncoder.get_encoder(kwargs.get("constant_encoder_name", None))
        constants_bytes = constant_encoder.encode(memory_layout)

        console.debug(f"[WebGPUDescriptorGenerator] constants encoded size: {len(constants_bytes)}[B]")

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

        return GraphExecutionData(graph, descriptor, constants_bytes)


def generate(graph: Graph, **kwargs):
    return WebGPUDescriptorGenerator.generate(graph, **kwargs)
