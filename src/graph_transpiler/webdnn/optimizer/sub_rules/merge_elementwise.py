from typing import Tuple, List

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.operators.merged_elementwise import MergedElementwise
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.util import flags


def find_elementwise_sub_graph(graph: Graph) -> List[Graph]:
    ops = traverse.filter_nodes(traverse.listup_operators(graph), Elementwise)  # type: List[Elementwise]
    sub_graphs = {op: Graph(list(op.inputs.values()), list(op.outputs.values())) for op in ops}
    result = {}

    while len(sub_graphs):
        out_node, sub_graph = list(sub_graphs.items())[0]
        del sub_graphs[out_node]

        flag_changed = False
        new_inputs = []
        for x in sub_graph.inputs:
            if (len(x.input_to) == 1) and (isinstance(x.output_from, Elementwise)):
                if x.output_from in sub_graphs:
                    del sub_graphs[x.output_from]

                if x.output_from in result:
                    del result[x.output_from]

                for i in range(len(x.output_from.inputs)):
                    new_inputs.append(x.output_from.inputs[f"x{i}"])

                flag_changed = True

            else:
                new_inputs.append(x)

        sub_graph.inputs = new_inputs

        if len(traverse.listup_operators(sub_graph)) > 1:
            if flag_changed:
                sub_graphs[out_node] = sub_graph
            else:
                result[out_node] = sub_graph

    return list(result.values())


class MergeElementwise(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        if not (flags.optimize.OPTIMIZE and flags.optimize.MERGE_ELEMENTWISE_OPERATION):
            return graph, False

        sub_graphs = find_elementwise_sub_graph(graph)
        if len(sub_graphs) == 0:
            return graph, False

        for sub_graph in sub_graphs:
            MergedElementwise(None, sub_graph)

        return graph, True
