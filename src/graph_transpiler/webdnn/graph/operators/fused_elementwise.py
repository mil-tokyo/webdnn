from typing import Optional

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.variable import Variable
from webdnn.graph.variables.constant_variable import ConstantVariable


class FusedElementwise(Elementwise):
    """
    Fused elementwise operator

    Before:

    ... code-block:: text

                                sub graph
                     +-------------------------------+
        -{op0}-> v1 -|-{op1}-> v2 -{op2}-> v3 -{op3}-|-> v4 -{op4}->
                     +-------------------------------+

    After:

    ... code-block:: text

        -{op0}-> v1 -{________FusedElementwise_______}-> v4 -{op4}->

                 A                                       A
                 :                                       :
                 : mapping                               : mapping
                 :                                       :
                 V                                       V
                     +-------------------------------+
                 v5 -|-{op1}-> v2 -{op2}-> v3 -{op3}-|-> v7
                     +-------------------------------+

    """

    def __init__(self, name: Optional[str], sub_graph: Graph):
        super().__init__(name)
        self.real2dummy = {}
        self.dummy2real = {}
        ops = traverse.listup_operators(sub_graph)

        dummy_xs = []
        for i, x in enumerate(sub_graph.inputs):
            dummy_x = self._create_dummy(x)
            for op in list(x.input_to):
                if op in ops:
                    op.replace_input(x, dummy_x)
            self.append_input(f"x{i}", x)

            dummy_xs.append(dummy_x)

        y = sub_graph.outputs[0]
        dummy_y = self._create_dummy(y)
        y.output_from.replace_output(y, dummy_y)
        self.append_output("y", y)

        self.sub_graph = Graph(dummy_xs, [dummy_y])

    def _create_dummy(self, v):
        if v in self.real2dummy:
            dummy = self.real2dummy[v]

        else:
            if isinstance(v, ConstantVariable):
                dummy = ConstantVariable(v.data, v.order)

            else:
                dummy = Variable(v.shape, v.order)

            self.real2dummy[v] = dummy
            self.dummy2real[dummy] = v

        return dummy

    def __call__(self):
        raise TypeError("FusedElementwise is not callable")
