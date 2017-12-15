from typing import List, Dict, Tuple, Set, Sequence, Union

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.backend.webgl.kernel_code import Type, ExpressionNode, Expression, IntExpressionNode, FloatExpressionNode
from webdnn.graph.axis import AxisKeyDict, Axis
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul


def change_order(expression: Expression, in_order: Order, out_order: Order) -> ExpressionNode:
    assert in_order.check_same_axes(out_order), f"""
"in_order" and "out_order" must have same axes:
    (in_order) = {in_order}
    (out_order) = {out_order}
"""

    if in_order == out_order:
        return ExpressionNode(expression)

    else:
        return ExpressionNode([expression, f".{''.join(['xyzw'[in_order.axes_dict[axis]] for axis in out_order.axes])}"])


def get_output_position(output_variable: Variable):
    if ChannelMode.get(output_variable) == ChannelModeEnum.R:
        return convert_position("gl_FragCoord.yx",
                                texture_shape(output_variable)[:2],
                                texture_stride(output_variable)[:2],
                                output_variable.shape,
                                output_variable.stride)

    elif ChannelMode.get(output_variable) == ChannelModeEnum.RGBA:
        return convert_position("vec3(gl_FragCoord.y, gl_FragCoord.x, 0)",
                                texture_shape(output_variable),
                                texture_stride(output_variable),
                                output_variable.shape,
                                output_variable.stride)


def convert_position(expression: Expression,
                     in_shape: Sequence[int], in_stride: Sequence[int],
                     out_shape: Sequence[int], out_stride: Sequence[int], index_offset: int = 0):
    if Placeholder.check_resolved(mul(in_shape)) and mul(in_shape) < 1 << 20:
        return ExpressionNode([
            "convert_position_fast(",
            expression, ",",
            ivec(in_stride), ", ",
            ivec(out_stride), ", ",
            ivec(out_shape), ", ",
            index_offset, ")"
        ])

    else:
        return ExpressionNode([
            "convert_position_i(",
            expression, ",",
            ivec(in_stride), ", ",
            ivec(out_stride), ", ",
            ivec(out_shape), ", ",
            index_offset, ")"
        ])


def convert_coord(expression: Expression,
                  in_shape: Sequence[int], in_stride: Sequence[int],
                  out_shape: Sequence[int], out_stride: Sequence[int], index_offset: int = 0):
    if all(Placeholder.check_resolved(v) for v in out_shape):
        inv_out_shape = [np.double(1.0) / np.double(v) for v in out_shape]

        return ExpressionNode([
            f"({Type.Vec.get_name(out_shape)}(", convert_position(expression, in_shape, in_stride, out_shape, out_stride, index_offset),
            ")",
            " + 0.5) * ", vec(inv_out_shape)
        ])

    else:
        return ExpressionNode([
            f"({Type.Vec.get_name(out_shape)}(", convert_position(expression, in_shape, in_stride, out_shape, out_stride, index_offset),
            ")",
            " + 0.5) / ", vec(out_shape)
        ])


def texel_fetch(variable: Variable, expression: Expression):
    texture_shape_xy = texture_shape(variable)[0:2][::-1]
    texture_stride_xy = texture_stride(variable)[0:2][::-1]
    return ExpressionNode([
        "texture2D(",
        variable, ",",
        convert_coord(expression, variable.shape, variable.stride, texture_shape_xy, texture_stride_xy), ")"
    ])


def ivec(sequence: Sequence[Union[int, Placeholder]]):
    assert 2 <= len(sequence) <= 4
    return [IntExpressionNode(v) for v in sequence]


def ivec2(sequence: Sequence[int]):
    assert len(sequence) == 2
    return ivec(sequence)


def ivec3(sequence: Sequence[int]):
    assert len(sequence) == 3
    return ivec(sequence)


def ivec4(sequence: Sequence[int]):
    assert len(sequence) == 4
    return ivec(sequence)


def vec(sequence: Sequence[float]):
    assert 2 <= len(sequence) <= 4
    return [FloatExpressionNode(v) for v in sequence]


def vec2(sequence: Sequence[float]):
    assert len(sequence) == 2
    return vec(sequence)


def vec3(sequence: Sequence[float]):
    assert len(sequence) == 3
    return vec(sequence)


def vec4(sequence: Sequence[float]):
    assert len(sequence) == 4
    return vec(sequence)


def _mod_snippet(t1: str, t2: str, tr: str):
    return f"{tr} mod({t1} x, {t2} p) {{ return x-(x/p)*p; }}"


def _convert_position_fast_snippet(ndim1: int, ndim2: int):
    dot = '+'.join(f'p1[{i}]*s1[{i}]' for i in range(ndim1))
    return f"""
ivec{ndim2} convert_position_fast(ivec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2, int offset) {{
    return mod(({dot} + offset) / s2, d2);
}}

ivec{ndim2} convert_position_fast(ivec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2) {{
    return convert_position_fast(p1, s1, s2, d2, 0);
}}

ivec{ndim2} convert_position_fast(vec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2, int offset) {{
    return convert_position_fast(ivec{ndim1}(p1), s1, s2, d2, offset);
}}

ivec{ndim2} convert_position_fast(vec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2) {{
    return convert_position_fast(ivec{ndim1}(p1), s1, s2, d2, 0);
}}
"""


def _convert_position_snippet(ndim1: int, ndim2: int):
    iteration_snippets = []
    for i in range(ndim1):
        iteration_snippets.append(f"""
            index += index_partial[{i}];
            m = index / s2;
            p2 += m;
            index -= m*s2;
        """)

    iteration_snippet = "\n".join(iteration_snippets)

    return f"""
ivec{ndim2} convert_position_i(ivec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2, int index_offset) {{
    ivec{ndim1} index_partial = p1 * s1;
    ivec{ndim2} index = ivec{ndim2}(index_offset);
    ivec{ndim2} p2 = ivec{ndim2}(0);

    ivec{ndim2} m;
    {iteration_snippet}

    return p2-(p2/d2)*d2;
}}

ivec{ndim2} convert_position_i(ivec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2) {{
    return convert_position_i(p1, s1, s2, d2, 0);
}}

ivec{ndim2} convert_position_i(vec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2, int index_offset) {{
    return convert_position_i(ivec{ndim1}(p1), s1, s2, d2, index_offset);
}}

ivec{ndim2} convert_position_i(vec{ndim1} p1, ivec{ndim1} s1, ivec{ndim2} s2, ivec{ndim2} d2) {{
    return convert_position_i(ivec{ndim1}(p1), s1, s2, d2, 0);
}}

ivec{ndim2} convert_position_i(vec{ndim1} p1, vec{ndim1} s1, vec{ndim2} s2, vec{ndim2} d2, int index_offset) {{
    return convert_position_i(ivec{ndim1}(p1), ivec{ndim1}(s1), ivec{ndim2}(s2), ivec{ndim2}(d2), index_offset);
}}

ivec{ndim2} convert_position_i(vec{ndim1} p1, vec{ndim1} s1, vec{ndim2} s2, vec{ndim2} d2) {{
    return convert_position_i(ivec{ndim1}(p1), ivec{ndim1}(s1), ivec{ndim2}(s2), ivec{ndim2}(d2), 0);
}}

vec{ndim2} convert_position(vec{ndim1} p1, vec{ndim1} s1, vec{ndim2} s2, vec{ndim2} d2, int index_offset) {{
    return vec{ndim2}(convert_position_i(ivec{ndim1}(p1), ivec{ndim1}(s1), ivec{ndim2}(s2), ivec{ndim2}(d2), index_offset)) + 0.5;
}}

vec{ndim2} convert_position(vec{ndim1} p1, vec{ndim1} s1, vec{ndim2} s2, vec{ndim2} d2) {{
    return convert_position(p1, s1, s2, d2, 0);
}}
"""


FragmentShaderPreamble = f"""
precision highp float;
precision highp int;
precision highp sampler2D;

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

{_convert_position_fast_snippet(2, 2)}
{_convert_position_fast_snippet(2, 3)}
{_convert_position_fast_snippet(2, 4)}
{_convert_position_fast_snippet(3, 2)}
{_convert_position_fast_snippet(3, 3)}
{_convert_position_fast_snippet(3, 4)}
{_convert_position_fast_snippet(4, 2)}
{_convert_position_fast_snippet(4, 3)}
{_convert_position_fast_snippet(4, 4)}
{_convert_position_snippet(2, 2)}
{_convert_position_snippet(2, 3)}
{_convert_position_snippet(2, 4)}
{_convert_position_snippet(3, 2)}
{_convert_position_snippet(3, 3)}
{_convert_position_snippet(3, 4)}
{_convert_position_snippet(4, 2)}
{_convert_position_snippet(4, 3)}
{_convert_position_snippet(4, 4)}

vec2 var2tex(vec2 var_position, vec2 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    vec3 tex_pos = convert_position(var_position, var_stride, tex_stride, tex_shape);
    return vec2(tex_pos.y, tex_pos.x);
}}
vec2 var2tex(vec3 var_position, vec3 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    vec3 tex_pos = convert_position(var_position, var_stride, tex_stride, tex_shape);
    return vec2(tex_pos.y, tex_pos.x);
}}
vec2 var2tex(vec4 var_position, vec4 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    vec3 tex_pos = convert_position(var_position, var_stride, tex_stride, tex_shape);
    return vec2(tex_pos.y, tex_pos.x);
}}


vec2 var2tex_coord(vec2 var_position, vec2 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    return var2tex(var_position, var_stride, tex_stride, tex_shape) / tex_shape.yx;
}}
vec2 var2tex_coord(ivec2 var_position, vec2 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    return var2tex(vec2(var_position), var_stride, tex_stride, tex_shape) / tex_shape.yx;
}}
vec2 var2tex_coord(vec3 var_position, vec3 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    return var2tex(var_position, var_stride, tex_stride, tex_shape) / tex_shape.yx;
}}
vec2 var2tex_coord(ivec3 var_position, vec3 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    return var2tex(vec3(var_position), var_stride, tex_stride, tex_shape) / tex_shape.yx;
}}
vec2 var2tex_coord(vec4 var_position, vec4 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    return var2tex(var_position, var_stride, tex_stride, tex_shape) / tex_shape.yx;
}}
vec2 var2tex_coord(ivec4 var_position, vec4 var_stride, vec3 tex_stride, vec3 tex_shape) {{
    return var2tex(vec4(var_position), var_stride, tex_stride, tex_shape) / tex_shape.yx;
}}


ivec2 tex2var(vec2 tex_position, vec3 tex_stride, vec2 var_stride, vec2 var_shape, int ch) {{
    return convert_position_i(vec3(tex_position.y, tex_position.x, float(ch) + 0.5), tex_stride, var_stride, var_shape);
}}
ivec3 tex2var(vec2 tex_position, vec3 tex_stride, vec3 var_stride, vec3 var_shape, int ch) {{
    return convert_position_i(vec3(tex_position.y, tex_position.x, float(ch) + 0.5), tex_stride, var_stride, var_shape);
}}
ivec4 tex2var(vec2 tex_position, vec3 tex_stride, vec4 var_stride, vec4 var_shape, int ch) {{
    return convert_position_i(vec3(tex_position.y, tex_position.x, float(ch) + 0.5), tex_stride, var_stride, var_shape);
}}

ivec2 tex2var(vec2 tex_position, vec3 tex_stride, vec2 var_stride, vec2 var_shape) {{
    return tex2var(tex_position, tex_stride, var_stride, var_shape, 0);
}}
ivec3 tex2var(vec2 tex_position, vec3 tex_stride, vec3 var_stride, vec3 var_shape) {{
    return tex2var(tex_position, tex_stride, var_stride, var_shape, 0);
}}
ivec4 tex2var(vec2 tex_position, vec3 tex_stride, vec4 var_stride, vec4 var_shape) {{
    return tex2var(tex_position, tex_stride, var_stride, var_shape, 0);
}}
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
    elements_per_pixel = ChannelMode.elements_per_pixel(v)
    width = (width + elements_per_pixel - 1) // elements_per_pixel
    return height, width, elements_per_pixel


def texture_stride(v: Variable):
    shape = texture_shape(v)
    return tuple(mul(shape[i + 1:]) for i in range(len(shape)))
