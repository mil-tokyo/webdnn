from typing import Optional

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.variable import Variable


class MergedElementwise(Elementwise):
    def __init__(self, name: Optional[str], sub_graph: Graph):
        super().__init__(name)
        self.sub_graph = sub_graph
        self.real2dummy = {}
        self.dummy2real = {}

        ops = traverse.listup_operators(sub_graph)

        inputs = set()
        dummy_inputs = []
        for op in ops:
            for variable in list(op.inputs.values()):
                if variable in sub_graph.inputs:
                    if variable in self.real2dummy:
                        dummy = self.real2dummy[variable]
                    else:
                        dummy = Variable(variable.shape, variable.order)
                        self.real2dummy[variable] = dummy
                        self.dummy2real[dummy] = variable
                        dummy_inputs.append(dummy)

                    op.replace_input(variable, dummy)
                    inputs.add(variable)

        for i, variable in enumerate(inputs):
            self.append_input(f"x{i}", variable)
        sub_graph.inputs = dummy_inputs

        variable = sub_graph.outputs[0]
        if variable in self.real2dummy:
            dummy = self.real2dummy[variable]
        else:
            dummy = Variable(variable.shape, variable.order)
            self.real2dummy[variable] = dummy
            self.dummy2real[dummy] = variable

        variable.output_from.replace_output(variable, dummy)
        self.append_output(f"y", variable)
        sub_graph.outputs = [dummy]

    def __call__(self):
        raise TypeError("MergedElementwise is not callable")
