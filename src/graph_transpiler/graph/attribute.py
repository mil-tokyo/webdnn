from graph_transpiler.graph.interface import INode, IAttribute


class Attribute(IAttribute):
    node: INode

    def __init__(self, node: INode):
        self.node = node
