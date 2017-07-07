from collections import namedtuple
from typing import List, Dict, Type, Union, Callable

from webdnn.backend.code_generator.allocator import MemoryLayout, Allocation
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import GPUSize, Kernel
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.operators.elementwise import Elementwise

RegisteredItem = namedtuple('RegisteredItem', ['OperatorClass', 'code', 'parameters'])
_registered_items = {}  # type: Dict[Type[Elementwise], RegisteredItem]


def _generate_source(xs: List[Allocation], y: Allocation, code: str, parameters: Dict[str, Union[int, float]]):
    input_variable_declaration_expression = "float y;"
    input_variable_declaration_expression += "\nfloat " + ", ".join(['x' + str(i) for i in range(len(xs))]) + ";"

    for varname, val in parameters.items():
        if isinstance(val, int):
            input_variable_declaration_expression += f"\nconst int {varname} = %%LOAD_BUFFER(elementwise_parameters_{varname})%%;"

        elif isinstance(val, float):
            input_variable_declaration_expression += \
                f"\nconst float {varname} = *((device float *)(&%%LOAD_BUFFER(elementwise_parameters_{varname})%%));"

        else:
            raise NotImplementedError

    for i in range(len(xs)):
        input_variable_declaration_expression += \
            f"\nconst device float *X{i} = %%LOAD_BUFFER(elementwise_Xs, {i})%%;"

    if all([x.variable.order == y.variable.order for x in xs]):
        calculate_index_expression = ""

        load_input_expression = ""
        for i in range(len(xs)):
            load_input_expression += f"\nx{i} = X{i}[i];"
    else:
        input_variable_declaration_expression += """
const char D = %%LOAD_BUFFER(elementwise_D)%%;
const device int *X_shapes = %%LOAD_BUFFER(elementwise_X_shapes)%%;
const device int *X_strides_in_Y = %%LOAD_BUFFER(elementwise_X_strides_in_Y)%%;"""

        calculate_index_expression = ""
        for i in range(len(xs)):
            calculate_index_expression += f"\nint i_x{i} = 0;"
        calculate_index_expression += "\nfor (int d = 0; d < D; d++) {"
        for i in range(len(xs)):
            calculate_index_expression += \
                f"\ni_x{i} = i_x{i} * X_shapes[D*{i} + d] + ((i / X_strides_in_Y[D*{i} + d]) % X_shapes[D*{i} + d]);"
        calculate_index_expression += "\n}"

        load_input_expression = ""
        for i in range(len(xs)):
            load_input_expression += f"\nx{i} = X{i}[i_x{i}];"

    return """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%% [[buffer(2)]],
                          uint index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    device float *Y = %%LOAD_BUFFER(elementwise_Y)%%;
    const int N = %%LOAD_BUFFER(elementwise_N)%%;

%%ELEMENTWISE_INPUT_VARIABLE_DECLARATIONS%%
    
    for (int i = index; i < N; i+= num_threads)
    {
%%ELEMENTWISE_INDEX_CALCULATION%%

%%ELEMENTWISE_LOAD_INPUT%%

        {
%%ELEMENTWISE_BODY%%
        }

        Y[i] = y;
    }
}
""" \
        .replace("%%ELEMENTWISE_INPUT_VARIABLE_DECLARATIONS%%", input_variable_declaration_expression) \
        .replace("%%ELEMENTWISE_INDEX_CALCULATION%%", calculate_index_expression) \
        .replace("%%ELEMENTWISE_LOAD_INPUT%%", load_input_expression) \
        .replace("%%ELEMENTWISE_BODY%%", code)


def elementwise_kernel(op: Elementwise, memory_layout: MemoryLayout) -> List[Kernel]:
    xs = [memory_layout[op.inputs[f"x{str(i)}"]] for i in range(len(op.inputs))]
    y = memory_layout[op.outputs["y"]]
    item = _registered_items[op.__class__]

    parameters = {key: fn(op) for key, fn in item.parameters.items()}

    x_shapes = [x.variable.shape for x in xs]

    y_strides = []
    stride = 1
    for s in reversed(y.variable.shape):
        y_strides.insert(0, stride)
        stride *= s

    # x_strides[i][j] is stride size of xs[i].order.axes[j] in y
    x_strides_in_y = [[] for _ in xs]
    for x, strides in zip(xs, x_strides_in_y):
        for axis in x.variable.order.axes:
            strides.append(y_strides[y.variable.order.axes_dict[axis]])

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "elementwise_Y": y,
        "elementwise_D": len(y.variable.shape),
        "elementwise_N": xs[0].variable.size,
        "elementwise_Xs": xs,
        "elementwise_X_strides_in_Y": x_strides_in_y,
        "elementwise_X_shapes": x_shapes
    })
    buffer_injector.register({
        f"elementwise_parameters_{key}": val for key, val in parameters.items()
    })

    name_injector = KernelNameInjector(op)

    source = _generate_source(xs, y, item.code, parameters)
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
        register_elementwise_kernel(ElementwiseSum, "y = x0 + x1;")

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
