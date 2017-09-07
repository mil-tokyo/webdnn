from typing import List, Dict, Type, Union, Callable

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.command_buffer import CommandBuffer
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.templates.elementwise import generate_elementwise_command_buffer, RegisteredItem
from webdnn.backend.webgpu.encode_command import encode_command
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph import traverse
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.fused_elementwise import FusedElementwise

_registered_items = {}  # type: Dict[Type[Elementwise], RegisteredItem]


@WebGPUDescriptorGenerator.register_handler(FusedElementwise)
def merged_elementwise_kernel(op: FusedElementwise, memory_layout: MemoryLayout) -> List[Kernel]:
    ops = traverse.listup_operators(op.sub_graph)
    builder, buffer_injector = generate_elementwise_command_buffer(ops,
                                                                   [_registered_items[op.__class__] for op in ops],
                                                                   memory_layout,
                                                                   dummy2real=op.dummy2real)
    return elementwise_kernel_base(op, builder, buffer_injector)


def elementwise_kernel(op: Elementwise, memory_layout: MemoryLayout) -> List[Kernel]:
    builder, buffer_injector = generate_elementwise_command_buffer([op],
                                                                   [_registered_items[op.__class__]],
                                                                   memory_layout)
    return elementwise_kernel_base(op, builder, buffer_injector)


def elementwise_kernel_base(op: Elementwise,
                            command_buffer: CommandBuffer,
                            buffer_injector: BufferInjector):
    name_injector = KernelNameInjector(op)

    source = encode_command(command_buffer)
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(8, 1, 1),
        GPUSize(MAX_THREADS_PER_THREADGROUP, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]


def register_elementwise_kernel(OperatorClass: Type[Elementwise],
                                code: str,
                                parameters: Dict[str, Callable[[Elementwise], Union[int, float]]] = None):
    """
    Utility function to define elementwise operation kernel in WebGPU backend.

    In code generation phase, registered `OperatorClass` operator is handled by
    :func:`webdnn.backend.webgpu.kernels.elementwise_kernel<elementwise_kernel>`, and kernel code is generated with `code`.::

        # With expression code
        register_elementwise_kernel(ElementwiseAdd, "y = x0 + x1;")

        # With block code
        register_elementwise_kernel(HardSigmoid, \"\"\"
            y = x0 * 0.2 + 0.5;
            if (y < 0.0) {
                y = 0.0;
            } else if (y > 1.0) {
                y = 1.0;
            }
        \"\"\")

        # With hyper parameters
        register_elementwise_kernel(ClippedRelu,
                                    "y = x0 < 0 ? 0 : x0 > cap ? cap : x0;",
                                    { "cap": lambda op: op.parameters["cap"] })

    Like above examples, `code` is only partial code to compute single output element. Other procedures such as memory load and store
    operation is not needed. variable `x0`, `x1`, ..., `x_{n-1}` and `y` is pre-defined, where `n` is number of input variables.

    If you want to use hyper parameters, use `parameters` argument like last one of above examples. Only int and float value are supported.

    Args:
        OperatorClass: Operator class which the handler is bound to
        code: Operator code in WebGPU (=Metal)
        parameters: Hyper parameters
    """
    WebGPUDescriptorGenerator.register_handler(OperatorClass)(elementwise_kernel)
    _registered_items[OperatorClass] = RegisteredItem(
        OperatorClass=OperatorClass,
        code=code,
        parameters={} if parameters is None else parameters
    )
