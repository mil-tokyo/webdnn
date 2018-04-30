from typing import NamedTuple, List, Sequence

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.concat import Concat
from webdnn.graph.operators.split_axis import SplitAxis
from webdnn.graph.operators.tensordot import Tensordot
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util.assertion import UnexpectedAndPleaseReportError
from webdnn.util.misc import mul


class GraphVars(NamedTuple):
    inputs: List[Variable]
    hidden: List[Variable]
    outputs: List[Variable]


def split_tensordot(graph: Graph, op: Tensordot, v: Variable, v_pair: Sequence[Variable], axis: Axis):
    s1 = v_pair[0].shape_dict[axis]
    s2 = v_pair[1].shape_dict[axis]
    A = op.inputs["A"]
    B = op.inputs["B"]
    C = op.outputs["C"]
    axes_M = tuple(filter(lambda a: a not in op.axes[0], A.order.axes))
    axes_N = tuple(filter(lambda a: a not in op.axes[1], B.order.axes))

    axes_K_A, axes_K_B = op.axes

    K = mul(A.shape_dict[a] for a in axes_K_A)
    M = A.size // K
    N = B.size // K

    shape_M = [A.shape_dict[a] for a in axes_M]
    shape_N = [B.shape_dict[a] for a in axes_N]

    op.remove_all()

    if v == A:
        A1, A2 = v_pair

        if axis in axes_K_A:
            split_axis_A = axis

            if (B.shape_dict[axes_K_B[0]] * s1) % (s1 + s2) == 0:
                split_axis_B = axes_K_B[0]

            else:
                # Factorize B's axes consisting to K into A's corresponding axes
                B = B.transpose(Order(axes_N + axes_K_B))
                B = B.reshape(order=Order((Axis(),) + axes_K_A), shape=[N] + [A.shape_dict[a] for a in axes_K_A])
                split_axis_B = split_axis_A
                axes_K_B = axes_K_A

            B1, B2 = SplitAxis(None, axis=split_axis_B, sections=[(B.shape_dict[split_axis_B] * s1) // (s1 + s2)])(B)

            C1, = Tensordot(None, [axes_K_A, axes_K_B])(A1, B1)
            C2, = Tensordot(None, [axes_K_A, axes_K_B])(A2, B2)
            OptimizeRule.replace_variable(graph,
                                          (C1 + C2).reshape(shape_M + shape_N, Order(axes_M + axes_N)).transpose_like(
                                              C), C)

        else:
            C1, = Tensordot(None, op.axes)(A1, B)
            C2, = Tensordot(None, op.axes)(A2, B)

            for a1, a2 in zip(C1.order.axes, C2.order.axes):
                if a1 == a2 == axis:
                    continue
                a1.unify(a2)

            C_new, = Concat(None, axis=axis)(C1, C2)
            OptimizeRule.replace_variable(graph, C_new, C)

    elif v == B:
        B1, B2 = v_pair

        if axis in axes_K_B:
            split_axis_B = axis

            if (A.shape_dict[axes_K_A[0]] * (s1 + s2)) % s1 == 0:
                split_axis_A = axes_K_A[0]

            else:
                # Factorize A's axes consisting to K into B's corresponding axes
                A = A.transpose(Order(axes_M + axes_K_A))
                A = A.reshape(order=Order((Axis(),) + axes_K_B), shape=[M] + [B.shape_dict[a] for a in axes_K_B])
                split_axis_A = split_axis_B
                axes_K_A = axes_K_B

            A1, A2 = SplitAxis(None, axis=split_axis_A, sections=[(A.shape_dict[split_axis_A] * s1) // (s1 + s2)])(A)

            C1, = Tensordot(None, [axes_K_A, axes_K_B])(A1, B1)
            C2, = Tensordot(None, [axes_K_A, axes_K_B])(A2, B2)
            OptimizeRule.replace_variable(graph,
                                          (C1 + C2).reshape(shape_M + shape_N, Order(axes_M + axes_N)).transpose_like(
                                              C), C)

        else:
            C1, = Tensordot(None, op.axes)(A, B1)
            C2, = Tensordot(None, op.axes)(A, B2)

            for a1, a2 in zip(C1.order.axes, C2.order.axes):
                if a1 == a2 == axis:
                    continue
                a1.unify(a2)

            C_new, = Concat(None, axis=axis)(C1, C2)
            OptimizeRule.replace_variable(graph, C_new, C)

    elif v == C:
        """
        before)

            C[M, N] = A[M, K] @ B[K, N]

        after) In case `axis` is in `N`,

            C[M, N1] = Concat(A[M, K] @ B1[K, N1])
            C[M, N2] = Concat(A[M, K] @ B2[K, N2])
        """
        raise NotImplementedError(f"Variable is too large to handle in WebGL backend: {v}")

    else:
        raise UnexpectedAndPleaseReportError
