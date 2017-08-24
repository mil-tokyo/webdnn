from typing import Tuple

from webdnn.backend.webgpu.operators.sgemm import Sgemm
from webdnn.graph import traverse
from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise_mul import ElementwiseMul
from webdnn.graph.operators.transpose import Transpose
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable
from webdnn.util import flags
from webdnn.util.misc import mul


class MergeSgemmAndElementwiseMul(OptimizeRule):
    """
    This optimize rule merges SGEMM weight and ElementwiseMul coefficient.

    ... code-block:: text

         x -+
            +-{sgemm}- h -+
        w1 -+             +-{mul}- y
                      w2 -+

    In above sub structure, if some conditions are satisfied, it can be simplified as follows,

    ... code-block::

              x -+
                 +-{sgemm}- y
        w1 * w2 -+

    Conditions are as follows.

        - :code:`w1` and :code:`w2` is :class:`~webdnn.graph.variables.constant_variable.ConstantVariable`.
        - All axes in :code:`w2` is derived from :code:`w1`

            Considering follow example,

            ... code-block::

                <x  shape=[5, 15], order=OrderNC>
                <w1 shape=[2, 3, 4, 5], order=OrderNHWC>

                <Sgemm A=w1, B=x,
                       M=24, K=5, N=15,
                       out_shape=[4, 6, 5, 3], out_order=OrderNCHW
                       transposeA=True, transposeB=True>

                <h shape=[4, 6, 5, 3] order=OrderNCHW>
                <w2 shape=[6] order=OrderC>

            In this case, :code:`w1` is regarded as `OrderMK` in SGEMM, and axis :code:`M` is split into :code:`N` and :code:`C` at the
            end of the SGEMM.

            ... code-block::

                                                    w1          |     x
                                          ======================|=============
                SGEMM's inputs' shape is:  [N:2, H:3, W:4, C:5] | [N:5, C:15]
                                          ----------------------+-------------
                SGEMM reshaped them as:             [M:24, K:5] | [K:5, N:15]
                                          ----------------------+-------------
                SGEMM's output shape is:                 [M:24, | N:15]
                                                     -----------+-------------
                SGEMM splits axes as:                [N:4, C:6, | H:5, W:3]
                                                                |
                w2's shape is:                            [C:6] |

            In this case, it can be said that "all axes in :code:`w2` (:code:`C`) is derived from :code:`w1`".

            :code:`w1` is reinterpreted as `OrderNCK` with shape :code:`(4, 6, 5)`. Also :code:`w2` is reinterpreted as `OrderNCK` with
            shape :code:`(1, 6, 1)`. Then, :code:`w1` and :code:`w2` are multiplied elementwisely.
    """

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.MERGE_SGEMM_AND_ELEMENTWISE_MUL,
        ]

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        flag_changed = False
        matches = traverse.search_sub_structure(graph, [Sgemm, Variable, ElementwiseMul])
        while len(matches) > 0:
            match = matches.pop()
            sgemm = match[0]  # type: Sgemm
            elementwise_mul = match[2]  # type:  ElementwiseMul

            out_order = sgemm.parameters["out_order"]
            out_shape = sgemm.parameters["out_shape"]

            axis_k = Axis('AxisK')

            if not isinstance(sgemm.inputs["A"], ConstantVariable) and not isinstance(sgemm.inputs["B"], ConstantVariable):
                # neither x nor w1 is constant
                continue

            elif isinstance(sgemm.inputs["A"], ConstantVariable):
                w1 = sgemm.inputs["A"]  # type: ConstantVariable

                if sgemm.transpose_A:
                    # w1.shape = (M, K)

                    shape = []
                    axes = []
                    for axis, size in zip(out_order.axes, out_shape):
                        shape.append(size)
                        axes.append(axis)

                        if mul(shape) >= sgemm.M:
                            break

                    if mul(shape) != sgemm.M:
                        # output axes are derived from both w1 and x
                        continue

                    w1_virtual_order = Order(axes + [axis_k])
                    w1_virtual_shape = shape + [sgemm.K]

                else:
                    # w1.shape = (K, M)

                    shape = [sgemm.K]
                    axes = [axis_k]
                    for axis, size in zip(out_order.axes, out_shape):
                        shape.append(size)
                        axes.append(axis)

                        if mul(shape) >= w1.size:
                            break

                    if mul(shape) != w1.size:
                        # output axes are derived from both w1 and x
                        continue

                    w1_virtual_order = Order(axes)
                    w1_virtual_shape = shape

            else:
                w1 = sgemm.inputs["B"]  # type: ConstantVariable

                if sgemm.transpose_B:
                    # w1.shape = (K, N)

                    shape = []
                    axes = []
                    for axis, size in reversed(list(zip(out_order.axes, out_shape))):
                        shape.insert(0, size)
                        axes.insert(0, axis)

                        if mul(shape) >= sgemm.N:
                            break

                    if mul(shape) != sgemm.N:
                        # output axes are derived from both w1 and x
                        continue

                    w1_virtual_order = Order([axis_k] + axes)
                    w1_virtual_shape = [sgemm.K] + shape

                else:
                    # w1.shape = (N, K)
                    shape = [sgemm.K]
                    axes = [axis_k]
                    for axis, size in reversed(list(zip(out_order.axes, out_shape))):
                        shape.insert(0, size)
                        axes.insert(0, axis)

                        if mul(shape) >= w1.size:
                            break

                    if mul(shape) != w1.size:
                        # output axes are derived from both w1 and x
                        continue

                    w1_virtual_order = Order(axes)
                    w1_virtual_shape = shape

            h = sgemm.outputs["C"]  # type: Variable

            x0 = elementwise_mul.inputs["x0"]
            x1 = elementwise_mul.inputs["x1"]
            if h == x1:
                if not isinstance(x0, ConstantVariable):
                    # w2 is not constant
                    continue

                w2 = x0  # type: ConstantVariable

            else:
                if not isinstance(x1, ConstantVariable):
                    # w2 is not constant
                    continue

                w2 = x1  # type: ConstantVariable

            y = elementwise_mul.outputs["y"]  # type: Variable

            if not all(axis in w1_virtual_order.axes for axis in w2.order.axes):
                # w2's axes are derived from both w1 and x
                continue

            elementwise_mul.remove_all()
            y_dummy, = Transpose(None)(h)
            y_dummy.change_order(y.order)
            y_dummy.replace(y)

            w2.change_order(w1_virtual_order)
            w_new = ConstantVariable(w1.data.reshape(w1_virtual_shape), w1_virtual_order) * w2  # type: ConstantVariable
            w1.data = w_new.data.reshape(w1.shape)

            flag_changed = True
            matches = traverse.search_sub_structure(graph, [Sgemm, Variable, ElementwiseMul])

        return graph, flag_changed
