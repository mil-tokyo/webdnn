from typing import Tuple

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.scalar_operation import ScalarOperation
from webdnn.graph.operators.scalar_add import ScalarAdd
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.scalar_mul import ScalarMul
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.traverse import search_sub_structure
from webdnn.graph.variable import Variable
from webdnn.util import flags, console


class ConcatScalarOperation(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not (flags.optimize.OPTIMIZE and flags.optimize.CONCAT_SCALAR_OPERATION):
            return graph, False

        flag_changed = False

        matches = search_sub_structure(graph, [ScalarOperation, Variable, ScalarOperation])
        while len(matches) > 0:
            match = matches[0]
            op1 = match[0]  # type: Operator
            op2 = match[2]  # type: Operator

            y1 = op1.outputs["y"]
            y2 = op2.outputs["y"]

            if isinstance(op1, ScalarAffine):
                if isinstance(op2, ScalarAffine):
                    op1.scale = op1.scale * op2.scale
                    op1.bias = op1.bias * op2.scale + op2.bias
                    op2.remove_all()
                    op1.replace_output(y1, y2)

                elif isinstance(op2, ScalarAdd):
                    op1.bias += op2.value
                    op2.remove_all()
                    op1.replace_output(y1, y2)

                elif isinstance(op2, ScalarMul):
                    op1.scale *= op2.value
                    op1.bias *= op2.value
                    op2.remove_all()
                    op1.replace_output(y1, y2)

                else:
                    console.debug(f"[ConcatScalarOperation] unhandled pair: {type(op1)} and {type(op2)}")

            elif isinstance(op1, ScalarAdd):
                if isinstance(op2, ScalarAffine):
                    op2.bias += op1.value * op2.scale
                    x = op1.inputs["x0"]
                    op1.remove_all()
                    x.replace(y1)

                elif isinstance(op2, ScalarAdd):
                    op1.parameters["value"] += op2.value
                    op2.remove_all()
                    op1.replace_output(y1, y2)

                elif isinstance(op2, ScalarMul):
                    x = op1.inputs["x0"]
                    new_op = ScalarAffine(None, scale=op2.value, bias=op1.value * op2.value)
                    new_y, = new_op(x)
                    op1.remove_all()
                    op2.remove_all()
                    y2.replace(new_y)

                else:
                    console.debug(f"[ConcatScalarOperation] unhandled pair: {type(op1)} and {type(op2)}")

            elif isinstance(op1, ScalarMul):
                if isinstance(op2, ScalarAffine):
                    op2.scale *= op1.value
                    x = op1.inputs["x0"]
                    op1.remove_all()
                    x.replace(y1)

                elif isinstance(op2, ScalarAdd):
                    x = op1.inputs["x0"]
                    new_op = ScalarAffine(None, scale=op1.value, bias=op2.value)
                    new_y, = new_op(x)
                    op1.remove_all()
                    op2.remove_all()
                    y2.replace(new_y)

                elif isinstance(op2, ScalarMul):
                    op1.parameters["value"] *= op2.value
                    op2.remove_all()
                    op1.replace_output(y1, y2)

                else:
                    console.debug(f"[ConcatScalarOperation] unhandled pair: {type(op1)} and {type(op2)}")

            flag_changed = True
            matches = search_sub_structure(graph, [ScalarAffine, Variable, ScalarAffine])

        return graph, flag_changed
