from collections import namedtuple
from typing import Type, Dict, Union, Sequence, Callable

from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode, GlobalDeclarationNode, Type as VType
from webdnn.backend.webgl.kernels.util import texture_stride, texture_shape, simplify_orders, convert_position, ivec, convert_coord
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.reduce import Reduce
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul

RegisteredItem = namedtuple('RegisteredItem', ['OperatorClass',
                                               'pre_reduction_snippet',
                                               'body_snippet',
                                               'post_reduction_snippet',
                                               'parameters'])
_registered_items = {}  # type: Dict[Type[Reduce], RegisteredItem]


def _generate_template(op: Reduce, reduction_size: int, shapes: Dict[Variable, Sequence[int]], strides: Dict[Variable, Sequence[int]]):
    x = op.inputs["x"]
    y = op.outputs["y"]

    params = []
    for key, callable in _registered_items[op.__class__].parameters.items():
        value = callable(op)
        params.append(GlobalDeclarationNode(VType.Float if isinstance(value, float) else VType.Int, key, value=value, with_value=True))

    return KernelCode([f"""
void main() {{
    ivec4 variable_position_y = """,
                       convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], shapes[y], strides[y]), f""";
    ivec4 variable_position_x = mod(variable_position_y, """, ivec(shapes[x]), f""");
    const int n_x = {reduction_size};
    float y;

    """, params, f"""
    """, _registered_items[op.__class__].pre_reduction_snippet, f"""

    for (int i_x = 0; i_x < {reduction_size}; i_x++) {{
        variable_position_x.w = i_x;
        float x = texture2D(""", x, ", ",
                       convert_coord(f"variable_position_x", shapes[x], strides[x], texture_shape(x)[:2][::-1],
                                     texture_stride(x)[:2][::-1]), f""").r;
        {{
            """, _registered_items[op.__class__].body_snippet, f"""
        }}
    }}

    """, _registered_items[op.__class__].post_reduction_snippet, f"""

    gl_FragColor.r = y;
}}
"""], name=op.__class__.__name__)


def register_reduction_kernel(OperatorClass: Type[Reduce],
                              body_snippet: str,
                              pre_reduction_snippet: str = "",
                              post_reduction_snippet: str = "",
                              parameters: Dict[str, Callable[[Reduce], Union[int, float]]] = None):
    """
    register reduction kernel

    you can use follow pre-defined variables in all snippets.

    - `y` output value.
    - `n_x` number of input elements (readonly).

    Also you can use follow variables only in body snippet.

    - `x` each input element (readonly)
    - `i_x` current `x`'s index (readonly)

    .. Examples:: Define a kernel which returns maximum value

        register_reduction_kernel(
            Max,
            pre_reduction_snippet="y = -1.0e10;",   // initialize "y" with very small value
            body_snippet="y = x > y ? x : y;",
        )

    """
    WebGLDescriptorGenerator.register_handler(OperatorClass)(reduce_kernel)
    _registered_items[OperatorClass] = RegisteredItem(
        OperatorClass=OperatorClass,
        pre_reduction_snippet=pre_reduction_snippet,
        body_snippet=body_snippet,
        post_reduction_snippet=post_reduction_snippet,
        parameters={} if parameters is None else parameters
    )


def reduce_kernel(op: Reduce):
    x = op.inputs["x"]
    y = op.outputs["y"]
    axis = op.axis

    orders, shape_dicts = simplify_orders([x, y], keep_axes=[axis])

    # Padding shapes and strides to 4D
    if orders[y].ndim > 4:
        raise NotImplementedError(f"Too large number of dimension: {y}")

    shapes = {v: [shape_dicts[v][a] for a in orders[v].axes] for v in [x, y]}
    strides = {v: [mul(shapes[v][orders[v].axes_dict[a] + 1:]) for a in orders[v].axes] for v in [x, y]}
    stride_dicts = {v: AxisKeyDict(orders[v].axes, strides[v]) for v in [x, y]}

    # Change x's shapes and strides order to same as y's order
    x_virtual_shape = [shape_dicts[x][a] if a in orders[x].axes else 1 for a in orders[y].axes]
    x_virtual_stride = [stride_dicts[x][a] if a in orders[x].axes else 1 for a in orders[y].axes]
    while len(x_virtual_shape) < 3:
        x_virtual_stride.append(1)
        x_virtual_shape.append(stride_dicts[x][axis])
    x_virtual_shape.append(shape_dicts[x][axis])
    x_virtual_stride.append(stride_dicts[x][axis])

    y_virtual_shape = shapes[y]
    y_virtual_stride = strides[y]
    while len(y_virtual_shape) < 4:
        y_virtual_stride.append(1)
        y_virtual_shape.append(1)

    code = _generate_template(op,
                              reduction_size=shape_dicts[x][axis],
                              shapes={y: y_virtual_shape, x: x_virtual_shape},
                              strides={y: y_virtual_stride, x: x_virtual_stride})
    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )]
