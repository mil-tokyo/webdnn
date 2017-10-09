from typing import Type, Dict, Callable, Union, List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.templates.elementwise import RegisteredItem
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import texture_stride, texture_shape, FragmentShaderPreamble, simplify_orders
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import Axis
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul

_registered_items = {}  # type: Dict[Type[Elementwise], RegisteredItem]


def _generate_template_no_convert_position(op: Elementwise):
    uniform_snippets = []
    load_snippets = []

    for k in op.inputs.keys():
        uniform_snippets.append(f"""
%%UNIFORM(sampler2D, sampler_{k})%%;
%%UNIFORM(vec2, texture_shape_{k})%%;
    """)
        load_snippets.append(f"""
float {k} = texture2D(sampler_{k}, gl_FragCoord.xy / texture_shape_{k}).r;
""")

    for key, callable in _registered_items[op.__class__].parameters.items():
        typename = "float" if isinstance(callable(op), float) else "int"

        uniform_snippets.append(f"""
%%UNIFORM({typename}, {key})%%;
""")

    body_snippet = _registered_items[op.__class__].code

    return FragmentShaderPreamble + "\n".join(uniform_snippets) + """

void main() {
    float y;

""" + "\n".join(load_snippets) + body_snippet + """

    gl_FragColor = vec4(y, 0, 0, 0);
}
"""


def _generate_template_convert_position(op: Elementwise):
    uniform_snippets = []
    load_snippets = []

    for k in op.inputs.keys():
        uniform_snippets.append(f"""
%%UNIFORM(sampler2D, sampler_{k})%%;
%%UNIFORM(vec2, texture_shape_{k})%%;
%%UNIFORM(vec2, texture_stride_{k})%%;
%%UNIFORM(vec4, variable_shape_{k})%%;
%%UNIFORM(vec4, variable_stride_{k})%%;
""")
        load_snippets.append(f"""
vec4 variable_position_{k} = mod(variable_position_y, variable_shape_{k});
vec2 texture_position_{k} = convert_coord(variable_position_{k}, variable_stride_{k}, texture_stride_{k}, texture_shape_{k});
float {k} = texture2D(sampler_{k}, texture_position_{k}).r;
""")

    for key, callable in _registered_items[op.__class__].parameters.items():
        typename = "float" if isinstance(callable(op), float) else "int"

        uniform_snippets.append(f"""
%%UNIFORM({typename}, {key})%%;
""")

    body_snippet = _registered_items[op.__class__].code

    return FragmentShaderPreamble + """
%%UNIFORM(vec2, texture_stride_y)%%;
%%UNIFORM(vec4, variable_shape_y)%%;
%%UNIFORM(vec4, variable_stride_y)%%;

""" + "\n".join(uniform_snippets) + """

void main() {
    float y;

    vec4 variable_position_y = convert_position(gl_FragCoord.xy, texture_stride_y, variable_stride_y, variable_shape_y);    

""" + "\n".join(load_snippets) + body_snippet + """

    gl_FragColor = vec4(y, 0, 0, 0);
}
"""


def register_elementwise_kernel(OperatorClass: Type[Elementwise],
                                code: str,
                                parameters: Dict[str, Callable[[Elementwise], Union[int, float]]] = None):
    WebGLDescriptorGenerator.register_handler(OperatorClass)(elementwise_kernel)
    _registered_items[OperatorClass] = RegisteredItem(
        OperatorClass=OperatorClass,
        code=code,
        parameters={} if parameters is None else parameters
    )


def _optimize_loop_structure(variables: List[Variable], key_variable: Variable, keep_axes: List[Axis] = None):
    """
    Optimize loop structure to iterate each element in variables

    Returns:
        (tuple): two elements are returned

        - First one is shape dictionary of all variables.
        - Second one is stride dictionary of all variables.
    """
    orders, shape_dicts = simplify_orders(variables,
                                          keep_axes=keep_axes)  # type: Dict[Variable, Order], Dict[Variable, AxisKeyDict[List[int]]]
    shapes = {v: [shape_dicts[v][a] for a in orders[v].axes] for v in variables}
    strides = {v: [mul(shapes[v][orders[v].axes_dict[a] + 1:]) for a in orders[v].axes] for v in variables}
    stride_dicts = {v: AxisKeyDict(orders[v].axes, strides[v]) for v in variables}

    # Re-ordering shapes and strides along to key variable's order
    axes = []
    axes += [axis for axis in orders[key_variable].axes if axis not in axes]
    for v in sorted(variables, key=lambda v: orders[v].ndim):
        axes += [axis for axis in orders[v].axes if axis not in axes]

    orders = {v: Order(list(filter(lambda x: x in orders[v].axes, axes))) for v in variables}

    key_order = orders[key_variable]
    shapes = {v: [shape_dicts[v][a] if a in orders[v].axes else 1 for a in key_order.axes] for v in variables}
    strides = {v: [stride_dicts[v][a] if a in orders[v].axes else 1 for a in key_order.axes] for v in variables}

    # Padding shapes and strides to 4D
    if key_order.ndim > 4:
        raise NotImplementedError(f"Too large number of dimension: {v}")

    for v in variables:
        shape = shapes[v]
        stride = strides[v]
        while len(shape) < 4:
            stride.append(1)
            shape.append(1)

    return shapes, strides


def elementwise_kernel(op: Elementwise):
    xs = list(op.inputs.values())
    y = op.outputs["y"]

    shapes, strides = _optimize_loop_structure(xs + [y], y)

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "texture_stride_y": texture_stride(y),
        "variable_shape_y": shapes[y],
        "variable_stride_y": strides[y]
    })

    for k, v in op.inputs.items():
        uniform_injector.register({
            f"sampler_{k}": v,
            f"texture_shape_{k}": texture_shape(v),
            f"texture_stride_{k}": texture_stride(v),
            f"variable_shape_{k}": shapes[v],
            f"variable_stride_{k}": strides[v],
        })

    for name, callable in _registered_items[op.__class__].parameters.items():
        uniform_injector.register({
            name: callable(op)
        })

    if all([x.shape == y.shape and x.order == y.order and texture_shape(x) == texture_shape(y) for x in xs]):
        # For all variables, not only element position (=logical position), pixel position (=actual position) is also same.
        # Therefore computing logical position is no need.
        source = _generate_template_no_convert_position(op)

    else:
        # Computing logical position is required.
        source = _generate_template_convert_position(op)

    source = uniform_injector.inject(source)
    source = name_injector.inject(source)
    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        y
    )

    return [kernel]
