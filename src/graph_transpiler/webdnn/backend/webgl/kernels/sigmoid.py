from typing import List, Dict, Tuple, Set

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import AxisKeyDict, Axis
from webdnn.graph.operators.sigmoid import Sigmoid
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul


def _simplify_orders(variables: List[Variable]) -> Tuple[Dict[Variable, Order], Dict[Variable, AxisKeyDict[int]]]:
    """
    Simplify variable orders based on follow rules

    - Axis whose size is :code:`1` will be removed.

    - If axis :code:`A` and :code:`B` is adjacent in all variables which has axis :code:`A` and axis :code:`B`, :code:`A` and :code:`B` will
      be merged.
        - For example, :code:`OrderABC` and :code:`OrderCAB` can be simplified as :code:`OrderXC` and :code:`OrderCX`
        - In this case, the size of axis :code:`X` is calculated as :code:`(size of axis A) * (size of axis B)`

    ...code-block::text

        ex)
            x0.order=NHWC,  simplify    x0.order=X
             y.order=NHWC ------------>  y.order=X

        ex)
            x0.order=C,     simplify    x0.order=C
            x1.order=NHWC ------------> x1.order=XC
             y.order=NHWC                y.order=XC

        ex)
            x0.order=C,     simplify    x0.order=C
            x1.order=HW   ------------> x1.order=X
             y.order=NHWC                y.order=NXC

    Returns:
        (tuple of dicts) simplified orders and shape
    """

    orders = {}  # type: Dict[Variable, Order]
    shape_dicts = {}  # type: Dict[Variable, AxisKeyDict[int]]
    axis_scalar = Axis("Scalar")

    # remove all axes whose size is `1`.
    for v in variables:
        new_axes = [a for a in v.order.axes if v.shape_dict[a] != 1]
        orders[v] = Order(new_axes)
        shape_dicts[v] = AxisKeyDict(new_axes, [v.shape_dict[a] for a in new_axes])

        if len(new_axes) == 0 and v.size == 1:
            orders[v] = Order([axis_scalar])
            shape_dicts[v] = {axis_scalar: 1}

    # list up all axes and variables which have the axis
    var_dict = AxisKeyDict[Set[Variable]]()
    for v in variables:
        for axis in orders[v].axes:
            if axis in var_dict:
                var_dict[axis].add(v)
            else:
                var_dict[axis] = {v}

    # find pair of axes which can be merged
    counter = 0
    flag_continue = True
    while flag_continue:
        flag_continue = False

        for axis1, vars1 in list(var_dict.items()):
            for axis2, vars2 in list(var_dict.items()):
                if axis1 == axis2:
                    continue

                if vars1 != vars2 or any(orders[v].axes_dict[axis1] + 1 != orders[v].axes_dict[axis2] for v in vars1):
                    # `axis1` and `axis2` must be adjacent.
                    continue

                # merge `axis1` and `axis2` into `axis_new`

                axis_new = Axis(f"X{counter}")
                counter += 1

                for v in vars1:
                    shape_dict = shape_dicts[v]
                    shape_dict[axis_new] = shape_dict[axis1] * shape_dict[axis2]
                    del shape_dict[axis1]
                    del shape_dict[axis2]

                    order = orders[v]
                    orders[v] = Order(order.axes[:order.axes_dict[axis1]] + (axis_new,) + order.axes[order.axes_dict[axis2] + 1:])

                var_dict[axis_new] = vars1
                del var_dict[axis1]
                del var_dict[axis2]

                flag_continue = True
                break

            if flag_continue:
                break

    return orders, shape_dicts


def _optimize_loop_structure(variables: List[Variable], key_variable: Variable):
    """
    Optimize loop structure to iterate each element in variables

    Returns:
        (tuple): two elements are returned

        - First one is shape dictionary of all variables.
        - Second one is stride dictionary of all variables.
    """
    orders, shape_dicts = _simplify_orders(variables)  # type: Dict[Variable, Order], Dict[Variable, AxisKeyDict[list[int]]]
    shapes = {v: [shape_dicts[v][a] for a in orders[v].axes] for v in variables}
    strides = {v: [mul(shapes[v][orders[v].axes_dict[a] + 1:]) for a in orders[v].axes] for v in variables}
    stride_dicts = {v: AxisKeyDict(orders[v].axes, strides[v]) for v in variables}

    # re-ordering
    axes = []
    for v in sorted(variables, key=lambda v: orders[v].ndim):
        axes += [axis for axis in orders[v].axes if axis not in axes]

    orders = {v: Order(list(filter(lambda x: x in orders[v].axes, axes))) for v in variables}
    shapes = {v: [shape_dicts[v][a] for a in orders[v].axes] for v in variables}
    strides = {v: [stride_dicts[v][a] for a in orders[v].axes] for v in variables}

    key_order = orders[key_variable]
    if key_order.ndim > 4:
        raise NotImplementedError('Currently, loop nest depth larger than 4 is not supported')

    for v in variables:
        shape = shapes[v]
        stride = strides[v]
        while len(shape) < 4:
            stride.append(1)
            shape.append(1)

    return shapes, strides


template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, X0)%%;

%%UNIFORM(vec2, d_y)%%;
%%UNIFORM(vec2, s_y)%%;
%%UNIFORM(vec4, d_Y)%%;
%%UNIFORM(vec4, s_Y)%%;

%%UNIFORM(vec2, d_x0)%%;
%%UNIFORM(vec2, s_x0)%%;
%%UNIFORM(vec4, d_X0)%%;
%%UNIFORM(vec4, s_X0)%%;

void main() {
    vec4 p_Y = convert_position(gl_FragCoord.xy, s_y, s_Y, d_Y);    
    vec4 p_X0 = mod(p_Y, d_X0); // for broadcasting
    vec2 p_x0 = convert_position(p_X0, s_X0, s_x0, d_x0);

    float x0 = texture2D(X0, p_x0 / d_x0).r;
    float y;
    
    // tanh is not supported in WebGL
    y = 1.0 / (1.0 + exp(-x0));

    gl_FragColor = vec4(y, 0, 0, 0);
}
"""


def texture_shape(v: Variable):
    # texture_length = (v.size + 4 - 1) // 4
    texture_length = v.size
    return [
        texture_length if texture_length < 2048 else 2048,
        (texture_length + 2048 - 1) // 2048
    ]


def texture_stride(v: Variable):
    result = []
    s = 1
    for d in texture_shape(v):
        result.append(s)
        s *= d
    return result


@WebGLDescriptorGenerator.register_handler(Sigmoid)
def elementwise_add(op: Sigmoid, _: MemoryLayout) -> List[Kernel]:
    x0 = op.inputs["x0"]
    y = op.outputs["y"]

    shapes, strides = _optimize_loop_structure([x0, y], y)

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()

    uniform_injector.register({
        "X0": x0,

        "s_y": texture_stride(y),
        "d_y": texture_shape(y),
        "d_Y": shapes[y],
        "s_Y": strides[y],

        "d_x0": texture_shape(x0),
        "s_x0": texture_stride(x0),
        "d_X0": shapes[x0],
        "s_X0": strides[x0],
    })

    source = template
    source = name_injector.inject(source)
    source = uniform_injector.inject(source)

    kernel = Kernel(
        source,
        name_injector.name,
        uniform_injector.samplers,
        uniform_injector.uniforms,
        y
    )

    return [kernel]
