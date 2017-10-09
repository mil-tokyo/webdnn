from typing import Tuple, Union

from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.zero_padding_2d import ZeroPadding2D
from webdnn.graph.optimize_rule import OptimizeRule
from webdnn.graph.traverse import search_sub_structure
from webdnn.graph.variable import Variable


class ConcatZeroPadding(OptimizeRule):
    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        """
        Merges padding of ZeroPadding2D and Convolution2D | MaxPooling2D | AveragePooling2D layer
        Args:
            graph:

        Returns:

        """
        # this optimization is always applied (since backends do not implement padding)
        flag_changed = False

        for tail_layer in [Convolution2D, MaxPooling2D, AveragePooling2D]:
            matches = search_sub_structure(graph, [ZeroPadding2D, Variable, tail_layer])
            while len(matches) > 0:
                match = matches[0]
                a1: ZeroPadding2D = match[0]
                a2: Union[Convolution2D, MaxPooling2D, AveragePooling2D] = match[2]

                zero_pad = a1.parameters["padding"]
                conv_pad = a2.parameters["padding"]
                a2.parameters["padding"] = (zero_pad[0] + conv_pad[0], zero_pad[1] + conv_pad[1])

                x1 = a1.inputs["x"]
                x2 = a2.inputs["x"]

                a1.remove_all()
                # replace_input checks if the shape of x1 and x2 are same, but this restriction does not hold.
                a2.remove_input(x2)
                a2.append_input("x", x1)

                flag_changed = True
                matches = search_sub_structure(graph, [ZeroPadding2D, Variable, tail_layer])

        return graph, flag_changed
