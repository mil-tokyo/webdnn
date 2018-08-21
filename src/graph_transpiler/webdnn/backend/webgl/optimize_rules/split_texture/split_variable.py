from typing import NamedTuple, List

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.attributes.texture_shape import TextureShape
from webdnn.backend.webgl.operators.partial_im2col import PartialIm2Col
from webdnn.backend.webgl.optimize_rules.split_texture.check_texture_size import SplitTarget
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_concat import split_concat
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_im2col import split_im2col
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_partial_im2col import split_partial_im2col
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_pooling_2d import split_pooling_2d
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_reshape import split_reshape
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_splitaxis import split_splitaxis
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_tensordot import split_tensordot
from webdnn.backend.webgl.optimize_rules.split_texture.operators.split_tensorwise import split_tensorwise
from webdnn.graph import traverse
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.tensorwise import Tensorwise
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.im2col import Im2Col
from webdnn.graph.operators.pooling_2d import Pooling2D
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.optimizer.sub_rules.constant_folding import ConstantFolding
from webdnn.util import console
from webdnn.util.misc import mul


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


class SplitVariable(OptimizeRule):
    def optimize(self, graph: Graph):
        flag_changed = False

        """
        Some operators does not support splitting, but only appear as constant.
        Workaround for such case, use ConstantFolding for limited operators even if it is turned off.
        """
        cf = ConstantFolding()
        graph, flag_changed_in_cf = cf.optimize(graph, (Transpose,))
        flag_changed |= flag_changed_in_cf

        c_before = traverse.filter_nodes(traverse.listup_variables(graph), ConstantVariable)
        c_size_before = sum([c.size for c in c_before])

        for v in traverse.filter_nodes(traverse.listup_variables(graph), SplitTarget):
            axis = _choose_split_axis(v)
            _split_axis(v, axis, graph)
            flag_changed = True

            c_after = traverse.filter_nodes(traverse.listup_variables(graph), ConstantVariable)
            c_size_after = sum([c.size for c in c_after])

            if c_size_before > c_size_after:
                raise Exception

        return graph, flag_changed


def _split_axis(v: Variable, axis: Axis, graph):
    """
    split variable by specified axis
    """
    s1 = v.shape_dict[axis] // 2
    s2 = v.shape_dict[axis] - s1

    if isinstance(v, ConstantVariable):
        v_datum = np.split(v.data, [s1], v.order.axes_dict[axis])
        v1 = ConstantVariable(v_datum[0], v.order)
        v2 = ConstantVariable(v_datum[1], v.order)

    else:
        v1 = Variable([s1 if a == axis else v.shape_dict[a] for a in v.order.axes], v.order)
        v2 = Variable([s2 if a == axis else v.shape_dict[a] for a in v.order.axes], v.order)

    ops = list(v.input_to)
    if v.output_from is not None:
        ops += [v.output_from]

    for op in ops:
        if isinstance(op, Tensordot):
            # NOTE:
            # "_split_tensordot" must be called before "_split_tensorwise".
            #
            # Let consider follow case:
            #
            #   A.order = [Axis.X, Axis.Y]
            #   B.order = [Axis.Y, Axis.Z]
            #   C, = Tensordot(None, [Axis.Y, Axis.Z])(A, B)  # -> C.order = [Axis.X, Axis.Y]
            #
            # In this case, tensordot operator has "Tensorwise[X]" and "Tensorwise[Y]" attributes, because "Tensordot" operation is
            # tensorwise operation for each output axis. However, "Axis.Y" is also contained in reduced axes in "A". Therefore,
            # "_split_tensorwise" incorrectly split "A".
            #
            split_tensordot(graph, op, v, [v1, v2], axis)

        elif Tensorwise.check_splittable(op, axis):
            split_tensorwise(graph, op, v, [v1, v2], axis)

        elif isinstance(op, SplitAxis):
            split_splitaxis(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Concat):
            split_concat(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Im2Col):
            split_im2col(graph, op, v, [v1, v2], axis)

        elif isinstance(op, PartialIm2Col):
            split_partial_im2col(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Reshape):
            split_reshape(graph, op, v, [v1, v2], axis)

        elif isinstance(op, Pooling2D):
            split_pooling_2d(graph, op, v, [v1, v2], axis)

        else:
            raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")


def _listup_splittable_axis(v: Variable, op: Operator) -> List[Axis]:
    if isinstance(op, (Concat, SplitAxis)):
        return list(v.order.axes)

    if isinstance(op, Reshape):
        """
        For more detail of this condition check, please see the comment document of `_split_reshape`
        """
        splittable_axes = []  # type: List[Axis]
        v1 = v
        v2 = op.outputs["y"] if v == op.inputs["x"] else op.inputs["x"]
        v1_order = op.in_order if v1 == op.inputs["x"] else op.out_order
        v2_order = op.in_order if v2 == op.inputs["x"] else op.out_order
        v1_shape = [v1.shape_dict[a] for a in v1_order.axes]

        for a1 in v1_order.axes:
            d1 = mul(v1_shape[v1_order.axes_dict[a1]:])
            d2 = 1
            axes = []
            for a2 in reversed(v2_order.axes):
                d2 *= v2.shape_dict[a2]
                axes.append(a2)

                if d2 == d1 and any(v2.shape_dict[a3] % 2 == 0 for a3 in axes):  # TODO
                    splittable_axes.append(a1)
                    continue

                elif d2 > d1:
                    continue

        return splittable_axes

    if isinstance(op, Im2Col):
        op = op  # type: Im2Col
        if v in op.outputs.values():
            return [Axis.N, Axis.H, Axis.W, Axis.C]

        else:
            return []

    if isinstance(op, PartialIm2Col):
        op = op  # type: PartialIm2Col
        if v in op.outputs.values():
            axes = [Axis.N, Axis.C]
            if op.axis not in axes:
                axes.append(op.axis)

            return axes

        else:
            return []

    if isinstance(op, Tensordot):
        return list(v.order.axes)

    if isinstance(op, Pooling2D):
        return [Axis.H, Axis.W]

    return []


def _choose_split_axis(v: Variable) -> Axis:
    """
    For too-large texture `v`, choose one axis which is the best one to reduce texture size by splitting `v` in that axis.

    Args:
        v: Variable, whose size is too large (= this variable has :code:`SplitTarget` attribute)

    Returns:
        axis
    """

    ops = list(v.input_to)
    if v.output_from is not None:
        ops += [v.output_from]

    splittable_axes = list(v.order.axes)
    for op in ops:
        _op_splittable_axes = _listup_splittable_axis(v, op) + [attr.axis for attr in op.get_attribute(Tensorwise)]
        for a in list(splittable_axes):
            if a not in _op_splittable_axes:
                splittable_axes.remove(a)

    if len(splittable_axes) == 0:
        raise ValueError("No axis is splittable")

    # Calculate the size of a side of texture which will be changed when each axis is split
    #
    # ex) OrderNC, N=512, C=2048, texture(width=2048, height=512)
    #     => If axis `N` is split, then height will be changed => N: 512 (=height)
    #        If axis `C` is split, then width will be changed => C: 2048 (=width)
    #
    # ex) OrderNCHW, N=1, C=512, H=13, W=13, texture(width=2048, height=43)
    #     => TexW == W*H*(partial of C) texture width consists of axis W, H and C.
    #        TexH == (partial of C)*N   texture height consists of axis C and N.
    #     => N cannot be split => N: -1
    #        C is related both width and height. In this case, use large one. => C: 2048
    #        H is included in width =>  H: 2048
    #        W is also included in width =>  W: 2048

    axis_corresponding_texture_size = AxisKeyDict()
    element_per_pixel = ChannelMode.elements_per_pixel(v)
    tex_h, tex_w = TextureShape.get(v)
    tex_w = (tex_w + element_per_pixel - 1) // element_per_pixel
    for a in v.order.axes:
        if v.shape_dict[a] == 1:
            # This axis cannot be split
            axis_corresponding_texture_size[a] = -1

        elif v.stride_dict[a] >= tex_w * element_per_pixel:
            axis_corresponding_texture_size[a] = tex_h

        elif v.stride_dict[a] * v.shape_dict[a] >= tex_w * element_per_pixel:
            axis_corresponding_texture_size[a] = max(tex_h, tex_w)

        else:
            axis_corresponding_texture_size[a] = tex_w

    splittable_axes.sort(key=lambda a: axis_corresponding_texture_size[a], reverse=True)
    target_axis = splittable_axes[0]

    console.debug(f"===========================================================================")
    console.debug(f"{v}")
    console.debug(f"  original order: {v.order}")
    console.debug(f"  original shape: {v.shape}")
    console.debug(f"   texture shape: {TextureShape.get(v)}")
    console.debug(f"")
    console.debug(f"  splittable axis: {splittable_axes}")
    console.debug(f"  split axis: {target_axis}")
    console.debug(f"")
    console.debug(f"  related operators:")
    for related_op in ops:
        console.debug(f"---------------------------------------------------------------------------")
        traverse.dump_op(related_op)
    console.debug(f"")

    if axis_corresponding_texture_size[target_axis] <= 0:
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    return target_axis
