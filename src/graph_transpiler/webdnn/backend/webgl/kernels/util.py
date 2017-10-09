from typing import List, Dict, Tuple, Set

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.graph.axis import AxisKeyDict, Axis
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable


def _mod_snippet(t1: str, t2: str, tr: str):
    return f"{tr} mod({t1} x, {t2} p) {{ return x-(x/p)*p; }}"


def _convert_position_i_snippet(t1: str, t2: str):
    ndim1 = int(t1[-1])

    iteration_snippets = []
    for i in range(ndim1):
        iteration_snippets.append(f"""
            index += index_partial[{i}];
            m = index / s2i;
            p2i += m;
            index -= m*s2i;
        """)

    iteration_snippet = "\n".join(iteration_snippets)

    return f"""
i{t2} convert_position_i({t1} p1, {t1} s1, {t2} s2, {t2} d2, int index_offset) {{
    i{t1} index_partial = i{t1}(p1) * i{t1}(s1);
    i{t2} s2i = i{t2}(s2);
    i{t2} d2i = i{t2}(d2);

    i{t2} index = i{t2}(index_offset);
    i{t2} p2i = i{t2}(0);
    
    i{t2} m;
    {iteration_snippet}

    return p2i-(p2i/d2i)*d2i;
}}

i{t2} convert_position_i({t1} p1, {t1} s1, {t2} s2, {t2} d2) {{
    return convert_position_i(p1, s1, s2, d2, 0);
}}
"""


def _convert_position_snippet(t1: str, t2: str):
    return f"""
{t2} convert_position({t1} p1, {t1} s1, {t2} s2, {t2} d2, int index_offset) {{
    return {t2}(convert_position_i(p1, s1, s2, d2, index_offset)) + 0.5;
}}

{t2} convert_position({t1} p1, {t1} s1, {t2} s2, {t2} d2) {{
    return convert_position(p1, s1, s2, d2, 0);
}}
"""


FragmentShaderPreamble = f"""
precision highp float;
precision highp int;

{_mod_snippet("int",   "int",   "int")}
{_mod_snippet("int",   "ivec2", "ivec2")}
{_mod_snippet("int",   "ivec3", "ivec3")}
{_mod_snippet("int",   "ivec4", "ivec4")}
{_mod_snippet("ivec2", "int",   "ivec2")}
{_mod_snippet("ivec3", "int",   "ivec3")}
{_mod_snippet("ivec4", "int",   "ivec4")}
{_mod_snippet("ivec2", "ivec2", "ivec2")}
{_mod_snippet("ivec3", "ivec3", "ivec3")}
{_mod_snippet("ivec4", "ivec4", "ivec4")}

{_convert_position_i_snippet("vec2", "vec2")}
{_convert_position_i_snippet("vec2", "vec3")}
{_convert_position_i_snippet("vec2", "vec4")}
{_convert_position_i_snippet("vec3", "vec2")}
{_convert_position_i_snippet("vec3", "vec3")}
{_convert_position_i_snippet("vec3", "vec4")}
{_convert_position_i_snippet("vec4", "vec2")}
{_convert_position_i_snippet("vec4", "vec3")}
{_convert_position_i_snippet("vec4", "vec4")}

{_convert_position_snippet("vec2", "vec2")}
{_convert_position_snippet("vec2", "vec3")}
{_convert_position_snippet("vec2", "vec4")}
{_convert_position_snippet("vec3", "vec2")}
{_convert_position_snippet("vec3", "vec3")}
{_convert_position_snippet("vec3", "vec4")}
{_convert_position_snippet("vec4", "vec2")}
{_convert_position_snippet("vec4", "vec3")}
{_convert_position_snippet("vec4", "vec4")}

vec2 convert_coord(vec2 p1, vec2 s1, vec2 s2, vec2 d2) {{ return fract((floor(dot(p1 - 0.5, s1) / s2) + 0.5) / d2); }}
vec4 convert_coord(vec2 p1, vec2 s1, vec4 s2, vec4 d2) {{ return fract((floor(dot(p1 - 0.5, s1) / s2) + 0.5) / d2); }}
vec2 convert_coord(vec4 p1, vec4 s1, vec2 s2, vec2 d2) {{ return fract((floor(dot(p1 - 0.5, s1) / s2) + 0.5) / d2); }}
vec4 convert_coord(vec4 p1, vec4 s1, vec4 s2, vec4 d2) {{ return fract((floor(dot(p1 - 0.5, s1) / s2) + 0.5) / d2); }}
"""


def simplify_orders(variables: List[Variable],
                    keep_axes: List[Axis] = None) -> Tuple[Dict[Variable, Order], Dict[Variable, AxisKeyDict[int]]]:
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
    if keep_axes is None:
        keep_axes = []

    orders = {}  # type: Dict[Variable, Order]
    shape_dicts = {}  # type: Dict[Variable, AxisKeyDict[int]]

    # remove all axes whose size is `1`.
    for v in variables:
        new_axes = [a for a in v.order.axes if v.shape_dict[a] != 1 or a in keep_axes]
        orders[v] = Order(new_axes)
        shape_dicts[v] = AxisKeyDict(new_axes, [v.shape_dict[a] for a in new_axes])

        if len(new_axes) == 0 and v.size == 1:
            orders[v] = Order([Axis(None)])
            shape_dicts[v] = AxisKeyDict(orders[v].axes, [1])

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
            if axis1 in keep_axes:
                # This axis must be kept
                continue

            for axis2, vars2 in list(var_dict.items()):
                if axis2 in keep_axes:
                    # This axis must be kept
                    continue

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
