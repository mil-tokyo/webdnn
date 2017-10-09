from collections import namedtuple
from typing import Type, Dict, Callable, Union

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import texture_stride, texture_shape, FragmentShaderPreamble, simplify_orders
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import AxisKeyDict
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.operators.reduce import Reduce
from webdnn.util.misc import mul

RegisteredItem = namedtuple('RegisteredItem', ['OperatorClass',
                                               'pre_reduction_snippet',
                                               'body_snippet',
                                               'post_reduction_snippet',
                                               'parameters'])
_registered_items = {}  # type: Dict[Type[Elementwise], RegisteredItem]


def _generate_template_convert_position(op: Reduce, reduction_size: int):
    uniform_snippets = [f"""
%%UNIFORM(sampler2D, sampler_x)%%;
%%UNIFORM(vec2, texture_shape_x)%%;
%%UNIFORM(vec2, texture_stride_x)%%;
%%UNIFORM(vec4, variable_shape_x)%%;
%%UNIFORM(vec4, variable_stride_x)%%;
"""]

    for key, callable in _registered_items[op.__class__].parameters.items():
        typename = "float" if isinstance(callable(op), float) else "int"

        uniform_snippets.append(f"%%UNIFORM({typename}, {key})%%;")

    pre_reduction_snippet = _registered_items[op.__class__].pre_reduction_snippet
    body_snippet = _registered_items[op.__class__].body_snippet
    post_reduction_snippet = _registered_items[op.__class__].post_reduction_snippet
    uniform_snippet = "\n".join(uniform_snippets)

    return FragmentShaderPreamble + f"""
%%UNIFORM(vec2, texture_stride_y)%%;
%%UNIFORM(vec4, variable_shape_y)%%;
%%UNIFORM(vec4, variable_stride_y)%%;

{uniform_snippet}

void main() {{

    vec4 variable_position_y = convert_position(gl_FragCoord.xy, texture_stride_y, variable_stride_y, variable_shape_y);    
    vec4 variable_position_x = mod(variable_position_y, variable_shape_x);  // broadcast
    
    const int n_x = {reduction_size};
    float y;
    
    {pre_reduction_snippet}

    for (int i_x = 0; i_x < {reduction_size}; i_x++) {{
        variable_position_x.w = float(i_x) + 0.5;
        float x = texture2D(sampler_x, convert_coord(variable_position_x, variable_stride_x, texture_stride_x, texture_shape_x)).r;

        {{
            {body_snippet}
        }}
    }}

    {post_reduction_snippet}
    
    gl_FragColor = vec4(y, 0, 0, 0);
}}
"""


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
            pre_reduction_snippet="y = -1.0e10;",   // initialize "y" with very smalle value
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

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "texture_stride_y": texture_stride(y),
        "variable_shape_y": y_virtual_shape,
        "variable_stride_y": y_virtual_stride,

        f"sampler_x": x,
        f"texture_shape_x": texture_shape(x),
        f"texture_stride_x": texture_stride(x),
        f"variable_shape_x": x_virtual_shape,
        f"variable_stride_x": x_virtual_stride,
    })

    for name, callable in _registered_items[op.__class__].parameters.items():
        uniform_injector.register({
            name: callable(op)
        })

    # Computing logical position is required.
    source = _generate_template_convert_position(op, reduction_size=shape_dicts[x][axis])

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
