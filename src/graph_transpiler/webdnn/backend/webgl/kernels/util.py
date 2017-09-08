from typing import List, Dict, Tuple, Set

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph.axis import AxisKeyDict, Axis
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul

FragmentShaderPreamble = """
precision highp float;

vec2 convert_position(vec2 p1, vec2 s1, vec2 s2, vec2 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec3 convert_position(vec2 p1, vec2 s1, vec3 s2, vec3 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec4 convert_position(vec2 p1, vec2 s1, vec4 s2, vec4 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec2 convert_position(vec3 p1, vec3 s1, vec2 s2, vec2 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec3 convert_position(vec3 p1, vec3 s1, vec3 s2, vec3 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec4 convert_position(vec3 p1, vec3 s1, vec4 s2, vec4 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec2 convert_position(vec4 p1, vec4 s1, vec2 s2, vec2 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec3 convert_position(vec4 p1, vec4 s1, vec3 s2, vec3 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }
vec4 convert_position(vec4 p1, vec4 s1, vec4 s2, vec4 d2) { return mod(floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5, d2); }

vec2 convert_coord(vec2 p1, vec2 s1, vec2 s2, vec2 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec3 convert_coord(vec2 p1, vec2 s1, vec3 s2, vec3 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec4 convert_coord(vec2 p1, vec2 s1, vec4 s2, vec4 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec2 convert_coord(vec3 p1, vec3 s1, vec2 s2, vec2 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec3 convert_coord(vec3 p1, vec3 s1, vec3 s2, vec3 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec4 convert_coord(vec3 p1, vec3 s1, vec4 s2, vec4 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec2 convert_coord(vec4 p1, vec4 s1, vec2 s2, vec2 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec3 convert_coord(vec4 p1, vec4 s1, vec3 s2, vec3 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
vec4 convert_coord(vec4 p1, vec4 s1, vec4 s2, vec4 d2) { return fract((floor((dot(p1 - 0.5, s1) + 0.5) / s2) + 0.5) / d2); }
"""


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
            shape_dicts[v] = AxisKeyDict([axis_scalar], [1])

    # list up all pair of axes and variables which have the corresponding axis
    var_dict = AxisKeyDict[Set[Variable]]()
    for v in variables:
        for axis in orders[v].axes:
            if axis in var_dict:
                var_dict[axis].add(v)
            else:
                var_dict[axis] = {v}

    # find pair of two axes which can be merged
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


def optimize_loop_structure(variables: List[Variable], key_variable: Variable):
    """
    Optimize loop structure to iterate each element in variables

    Returns:
        (tuple): two elements are returned

        - First one is shape dictionary of all variables.
        - Second one is stride dictionary of all variables.
    """
    orders, shape_dicts = _simplify_orders(variables)  # type: Dict[Variable, Order], Dict[Variable, AxisKeyDict[List[int]]]
    shapes = {v: [shape_dicts[v][a] for a in orders[v].axes] for v in variables}
    strides = {v: [mul(shapes[v][orders[v].axes_dict[a] + 1:]) for a in orders[v].axes] for v in variables}
    stride_dicts = {v: AxisKeyDict(orders[v].axes, strides[v]) for v in variables}

    # re-ordering
    axes = []
    for v in sorted(variables, key=lambda v: orders[v].ndim):
        axes += [axis for axis in orders[v].axes if axis not in axes]

    orders = {v: Order(list(filter(lambda x: x in orders[v].axes, axes))) for v in variables}
    key_order = orders[key_variable]

    if key_order.ndim > 4:
        raise NotImplementedError('Currently, loop nest depth larger than 4 is not supported')

    shapes = {v: [shape_dicts[v][a] if a in orders[v].axes else 1 for a in key_order.axes] for v in variables}
    strides = {v: [stride_dicts[v][a] if a in orders[v].axes else 1 for a in key_order.axes] for v in variables}

    for v in variables:
        shape = shapes[v]
        stride = strides[v]
        while len(shape) < 4:
            stride.append(1)
            shape.append(1)

    return shapes, strides


def texture_shape(v: Variable):
    height, width = TextureShape.get(v)
    return [width, height]


def texture_stride(v: Variable):
    result = []
    channel_mode = ChannelMode.get(v)
    if channel_mode == ChannelModeEnum.R:
        s = 1

    elif channel_mode == ChannelModeEnum.RGBA:
        s = 4

    else:
        raise NotImplementedError(f"Unknown channel mode: {channel_mode}")

    for d in texture_shape(v):
        result.append(s)
        s *= d
    return result
