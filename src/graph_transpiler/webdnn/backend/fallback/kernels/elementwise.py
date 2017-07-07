from collections import namedtuple
from typing import List, Dict, Type, Union, Callable

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.fallback.generator import FallbackDescriptorGenerator
from webdnn.backend.fallback.kernel import Kernel
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.variable import Variable

RegisteredItem = namedtuple('RegisteredItem', ['OperatorClass', 'code', 'parameters'])
_registered_items = {}  # type: Dict[Type[Elementwise], RegisteredItem]


def _generate_source(xs: List[Variable], expression: str, parameters: Dict[str, Union[int, float]]):
    inputs_expression = ",".join([f"x{i}" for i in range(len(xs))])
    for varname in parameters.keys():
        inputs_expression += f", {varname}"

    call_args_expression = ",".join([f"xs[{i}]" for i in range(len(xs))])
    for varname in parameters.keys():
        call_args_expression += f", option.elementwise_parameters_{varname}"

    return """
%%FUNC_NAME%%: function(input_arrays, output_arrays, option) {
    var x_shapes = option.x_shapes;
    var x_strides_in_y = option.x_strides_in_y;
    
    var y = 0;
    var xs = [];
    var i_xs = [];    
    var i = 0, n = 0, d = 0;
    
    for (i = 0; i < output_arrays[0].length; i++) {
        for (n = 0; n < input_arrays.length; n++) {
            i_xs[n] = 0;
        }
        for (d = 0; d < x_shapes[0].length; d++) {
            for (n = 0; n < input_arrays.length; n++) {
                i_xs[n] = i_xs[n] * x_shapes[n][d] + (Math.floor(i / x_strides_in_y[n][d]) % x_shapes[n][d]);
            }
        }
        for (n = 0; n < input_arrays.length; n++) {
            xs[n] = input_arrays[n][i_xs[n]];
        }

        y = (function(){
            var y = 0;

            (function(%%ELEMENTWISE_INPUTS%%){
                %%ELEMENTWISE_BODY%%
            })(%%ELEMENTWISE_CALL_ARGS%%);
            
            return y;
        })();

        output_arrays[0][i] = y;
    }
}
""" \
        .replace("%%ELEMENTWISE_INPUTS%%", inputs_expression) \
        .replace("%%ELEMENTWISE_CALL_ARGS%%", call_args_expression) \
        .replace("%%ELEMENTWISE_BODY%%", expression)


# noinspection PyUnusedLocal
def elementwise_kernel(op: Elementwise, memory_layout: MemoryLayout) -> List[Kernel]:
    xs = [op.inputs[f"x{str(i)}"] for i in range(len(op.inputs))]
    y = op.outputs["y"]
    item = _registered_items[op.__class__]

    parameters = {key: fn(op) for key, fn in item.parameters.items()}

    x_shapes = [x.shape for x in xs]

    y_strides = []
    stride = 1
    for s in reversed(y.shape):
        y_strides.insert(0, stride)
        stride *= s

    # x_strides[i][j] is stride size of xs[i].order.axes[j] in y
    x_strides_in_y = [[] for _ in xs]
    for x, strides in zip(xs, x_strides_in_y):
        for axis in x.order.axes:
            strides.append(y_strides[y.order.axes_dict[axis]])

    call_options = {
        "x_shapes": x_shapes,
        "x_strides_in_y": x_strides_in_y
    }
    call_options.update({f"elementwise_parameters_{key}": val for key, val in parameters.items()})

    name_injector = KernelNameInjector(op)

    source = _generate_source(xs, item.code, parameters)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        inputs=xs,
        outputs=[y],
        call_option=call_options
    )

    return [kernel]


def register_elementwise_kernel(OperatorClass: Type[Elementwise],
                                code: str,
                                parameters: Dict[str, Callable[[Elementwise], Union[int, float]]] = None):
    """
    Utility function to define elementwise operation kernel in Fallback backend.

    In code generation phase, registered `OperatorClass` operator is handled by
    :func:`webdnn.backend.fallback.kernels.elementwise_kernel<elementwise_kernel>`, and kernel code is generated with `code`.::

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
        code: Operator code in JavaScript
        parameters: Hyper parameters
    """
    FallbackDescriptorGenerator.register_handler(OperatorClass)(elementwise_kernel)
    _registered_items[OperatorClass] = RegisteredItem(
        OperatorClass=OperatorClass,
        code=code,
        parameters={} if parameters is None else parameters
    )
