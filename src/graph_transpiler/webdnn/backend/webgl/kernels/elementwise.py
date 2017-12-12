from typing import Type, Dict, Callable, Union, List, Sequence

from webdnn.backend.code_generator.templates.elementwise import RegisteredItem
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, GlobalDeclarationNode, Type as VType
from webdnn.backend.webgl.kernels.util import texture_stride, texture_shape, simplify_orders, vec2, convert_position, convert_coord, ivec
from webdnn.graph.axis import Axis
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul

_registered_items = {}  # type: Dict[Type[Elementwise], RegisteredItem]


def _generate_template_no_convert_position(op: Elementwise):
    load_nodes = []
    for k, v in op.inputs.items():
        load_nodes += [f"float {k} = texture2D(", v, ", gl_FragCoord.xy / ", vec2(texture_shape(v)[:2][::-1]), ").r;\n"]

    for key, callable in _registered_items[op.__class__].parameters.items():
        value = callable(op)
        load_nodes.append(GlobalDeclarationNode(VType.Float if isinstance(value, float) else VType.Int, key, value=value, with_value=True))

    return KernelCode(["""
void main() {
    float y;

""", load_nodes, _registered_items[op.__class__].code, """

    gl_FragColor = vec4(y, 0, 0, 0);
}
"""], name=op.__class__.__name__)


def _generate_template_convert_position(op: Elementwise, shapes: Dict[Variable, Sequence[int]], strides: Dict[Variable, Sequence[int]]):
    load_nodes = []
    y = op.outputs["y"]

    for k, v in op.inputs.items():
        if shapes[v] == shapes[y]:
            load_nodes += [
                f"float {k} = texture2D(", v, ", ",
                convert_coord(f"variable_position_y", shapes[v], strides[v], texture_shape(v)[:2][::-1], texture_stride(v)[:2][::-1]),
                ").r;\n"]

        else:
            load_nodes += [f"ivec4 variable_position_{k} = mod(variable_position_y, ", ivec(shapes[v]), f");\n"]
            load_nodes += [
                f"float {k} = texture2D(", v, ", ",
                convert_coord(f"variable_position_{k}", shapes[v], strides[v], texture_shape(v)[:2][::-1], texture_stride(v)[:2][::-1]),
                ").r;\n"]

    for key, callable in _registered_items[op.__class__].parameters.items():
        value = callable(op)
        load_nodes.append(GlobalDeclarationNode(VType.Float if isinstance(value, float) else VType.Int, key, value=value, with_value=True))

    return KernelCode(["""
void main() {
    float y;

    ivec4 variable_position_y = """,
                       convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], shapes[y], strides[y]), """;

""", load_nodes, _registered_items[op.__class__].code, """

    gl_FragColor = vec4(y, 0, 0, 0);
}
"""], name=op.__class__.__name__)


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

    if all([x.shape == y.shape and x.order == y.order and texture_shape(x) == texture_shape(y) for x in xs]):
        # For all variables, not only element position (=logical position), pixel position (=actual position) is also same.
        # Therefore computing logical position is no need.
        code = _generate_template_no_convert_position(op)

    else:
        # Computing logical position is required.
        code = _generate_template_convert_position(op, shapes, strides)

    source = code.generate()
    kernel = Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )

    return [kernel]
