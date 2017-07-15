from collections import namedtuple
from typing import List, Dict, Type, Union, Callable, Any

from webdnn.backend.code_generator.allocator import MemoryLayout, Allocation
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph import traverse
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.merged_elementwise import MergedElementwise
from webdnn.graph.variable import Variable

RegisteredItem = namedtuple('RegisteredItem', ['OperatorClass', 'code', 'parameters'])
_registered_items = {}  # type: Dict[Type[Elementwise], RegisteredItem]


def _generate_source(xs: List[Allocation], y: Allocation, codes: List[List[Any]], parameters: Dict[str, Union[int, float]]):
    flag_same_order = all([x.variable.order == y.variable.order for x in xs])

    variable_declaration_expression = "\n".join(
        [f"const float *X{i} = %%LOAD_BUFFER(elementwise_Xs, {i})%%;" for i in range(len(xs))])

    if flag_same_order:
        calculate_index_expression = ""

    else:
        variable_declaration_expression += """
const char D = %%LOAD_BUFFER(elementwise_D)%%;
const int *X_shapes = %%LOAD_BUFFER(elementwise_X_shapes)%%;
const int *X_strides_in_Y = %%LOAD_BUFFER(elementwise_X_strides_in_Y)%%;"""

        calculate_index_expression = ""
        for i in range(len(xs)):
            calculate_index_expression += f"\nint i_x{i} = 0;"
        calculate_index_expression += "\nfor (int d = 0; d < D; d++) {"
        for i in range(len(xs)):
            calculate_index_expression += \
                f"\ni_x{i} = i_x{i} * X_shapes[D*{i} + d] + ((i / X_strides_in_Y[D*{i} + d]) % X_shapes[D*{i} + d]);"
        calculate_index_expression += "\n}"

    elementwise_body = []
    for code in codes:
        if code[0] == "declare":
            # ("declare", name, type)
            elementwise_body.append(f"{code[2]} {code[1]};")

        elif code[0] == "loadX":
            #  ("loadX", varname, buffer_index)
            if flag_same_order:
                elementwise_body.append(f"{code[1]} = X{code[2]}[i]; // {code}")

            else:
                elementwise_body.append(f"{code[1]} = X{code[2]}[i_x{code[2]}]; // {code}")

        elif code[0] == "loadP":
            #  ("loadP", varname, meta_name)
            varname = code[1]
            value = parameters[code[2]]
            if isinstance(value, int):
                elementwise_body.append(f"const int {varname} = %%LOAD_BUFFER({code[2]})%%; // {code}")

            elif isinstance(value, float):
                elementwise_body.append(f"const float {varname} = *((float *)(&%%LOAD_BUFFER({code[2]})%%)); // {code}")

            else:
                raise NotImplementedError

        elif code[0] == "storeY":
            #  ("storeY")
            elementwise_body.append("Y[i] = y;")

        elif code[0] == "rename":
            #  ("rename", old_name, new_name)
            elementwise_body.append(f"{code[2]} = {code[1]}; // {code}")

        elif code[0] == "enterBlock":
            #  ("enterBlock")
            elementwise_body.append("{")

        elif code[0] == "exitBlock":
            #  ("exitBlock")
            elementwise_body.append("}")

        elif code[0] == "exec":
            #  ("exec", OperatorClass)
            elementwise_body.append(f"// ('exec', {code[1].__name__})")
            elementwise_body.append(_registered_items[code[1]].code)

        else:
            raise NotImplementedError(f"Unknown OP code: {code}")

    elementwise_body = "\n".join(elementwise_body)

    return """
void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
    float *Y = %%LOAD_BUFFER(elementwise_Y)%%;
    const int N = %%LOAD_BUFFER(elementwise_N)%%;

%%ELEMENTWISE_VARIABLE_DECLARATIONS%%

    for (int i = 0; i < N; i++)
    {
%%ELEMENTWISE_INDEX_CALCULATION%%

%%ELEMENTWISE_BODY%%
    }
}
    """ \
        .replace("%%ELEMENTWISE_VARIABLE_DECLARATIONS%%", variable_declaration_expression) \
        .replace("%%ELEMENTWISE_INDEX_CALCULATION%%", calculate_index_expression) \
        .replace("%%ELEMENTWISE_BODY%%", elementwise_body)


@WebassemblyDescriptorGenerator.register_handler(MergedElementwise)
def merged_elementwise_kernel(op: MergedElementwise, memory_layout: MemoryLayout) -> List[Kernel]:
    xs = []
    y = None

    codes = []
    parameters = {}
    name2variable = {}
    variable2name = {}
    retain_count = {}  # type: Dict[str, int]

    def rename(old_name, new_name):
        v = name2variable[old_name]
        codes.append(("rename", old_name, new_name))
        variable2name[v] = new_name
        name2variable[new_name] = v
        name2variable[old_name] = None
        retain_count[new_name] = retain_count[old_name]
        retain_count[old_name] = 0

    def declare(name):
        codes.append(("declare", name, "float"))
        name2variable[name] = None
        retain_count[name] = 0

    def escape(name):
        i = 0
        while True:
            temp = f"temp{i}"
            if temp not in name2variable:
                declare(temp)
                break

            if retain_count[temp] == 0:
                break

            i += 1
        rename(name, temp)

    for sub_op in traverse.listup_operators(op.sub_graph):
        for name, x in sub_op.inputs.items():  # type: str, Variable
            if x in op.dummy2real:
                x = op.dummy2real[x]

            if name in name2variable:
                if retain_count[name] > 0:
                    # Escape loaded value into another name to avoid loading overhead
                    escape(name)

            else:
                declare(name)

            if x in variable2name:
                if variable2name[x] == name:
                    # Already loaded as correct name
                    pass

                else:
                    # Loaded as other name
                    rename(variable2name[x], name)

            else:
                # Not loaded
                codes.append(("loadX", name, len(xs)))
                variable2name[x] = name
                name2variable[name] = x
                retain_count[name] = len(x.input_to)
                xs.append(x)

        if "y" in name2variable:
            if retain_count["y"] > 0:
                # Escape intermediate calculated value
                escape("y")

        else:
            declare("y")

        codes.append(("enterBlock",))

        for varname, fn in _registered_items[sub_op.__class__].parameters.items():
            meta_name = f"elementwise_parameters{len(parameters)}"
            value = fn(sub_op)
            parameters[meta_name] = value
            codes.append(("loadP", varname, meta_name))

        codes.append(("exec", sub_op.__class__))
        y = sub_op.outputs["y"]  # type: Variable
        if y in op.dummy2real:
            y = op.dummy2real[y]
        variable2name[y] = "y"
        name2variable["y"] = y
        retain_count["y"] = len(y.input_to)

        for name in sub_op.inputs:
            retain_count[name] -= 1

        codes.append(("exitBlock",))

    codes.append(("storeY",))
    retain_count["y"] -= 1

    xs = [memory_layout[x] for x in xs]
    y = memory_layout[y]
    return elementwise_kernel_base(op, xs, y, codes, parameters)


def elementwise_kernel(op: Elementwise, memory_layout: MemoryLayout) -> List[Kernel]:
    xs = [memory_layout[op.inputs[f"x{str(i)}"]] for i in range(len(op.inputs))]
    y = memory_layout[op.outputs["y"]]

    codes = []
    parameters = {}
    for i in range(len(xs)):
        codes.append(("declare", f"x{i}", "float"))
        codes.append(("loadX", f"x{i}", i))

    codes.append(("declare", "y", "float"))
    codes.append(("enterBlock",))

    for varname, fn in _registered_items[op.__class__].parameters.items():
        meta_name = f"elementwise_parameters{len(parameters)}"
        value = fn(op)
        parameters[meta_name] = value
        codes.append(("loadP", varname, meta_name))

    codes.append(("exec", op.__class__))
    codes.append(("exitBlock",))
    codes.append(("storeY",))

    return elementwise_kernel_base(op, xs, y, codes, parameters)


def elementwise_kernel_base(op: Elementwise,
                            xs: List[Allocation],
                            y: Allocation,
                            codes: List[List[Any]],
                            parameters: Dict[str, Union[int, float]]):
    buffer_injector = BufferInjector()
    buffer_injector.register({
        "elementwise_Y": y,
        "elementwise_D": len(y.variable.shape),
        "elementwise_N": xs[0].variable.size,
        "elementwise_Xs": xs,
        "elementwise_X_strides_in_Y": [[y.variable.stride_dict[axis] for axis in x.variable.order.axes] for x in xs],
        "elementwise_X_shapes": [x.variable.shape for x in xs]
    })
    buffer_injector.register(parameters)

    name_injector = KernelNameInjector(op)

    source = _generate_source(xs, y, codes, parameters)
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]


def register_elementwise_kernel(OperatorClass: Type[Elementwise],
                                code: str,
                                parameters: Dict[str, Callable[[Elementwise], Union[int, float]]] = None):
    """
    Utility function to define elementwise operation kernel in WebAssembly backend.

    In code generation phase, registered `OperatorClass` operator is handled by
    :func:`webdnn.backend.webassembly.kernels.elementwise_kernel<elementwise_kernel>`, and kernel code is generated with `code`.::

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
        code: Operator code in C++
        parameters: Hyper parameters
    """
    WebassemblyDescriptorGenerator.register_handler(OperatorClass)(elementwise_kernel)
    _registered_items[OperatorClass] = RegisteredItem(
        OperatorClass=OperatorClass,
        code=code,
        parameters={} if parameters is None else parameters
    )
