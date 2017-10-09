from typing import Tuple

from webdnn.graph import traverse
from webdnn.graph.graph import Graph
from webdnn.graph.optimize_rule import OptimizeRule


class DumpGraph(OptimizeRule):
    """
    Dump current computation graph

    Attributes:
        filename (str): Name of dumped dot file. You can use `{count}` placeholder, which will be replaced with the incremental counter.
            For example, "cg_{count}.dot" means the file name "cg_0.dot", "cg_1.dot", ...
    """

    def __init__(self, filename: str = "cg.dot"):
        self.filename = filename
        self.counter = 0

    def optimize(self, graph: Graph) -> Tuple[Graph, bool]:
        filename = self.filename.replace("{count}", str(self.counter))
        with open(filename, "w") as f:
            f.write(traverse.dump_dot(graph))

        self.counter += 1

        return graph, False
