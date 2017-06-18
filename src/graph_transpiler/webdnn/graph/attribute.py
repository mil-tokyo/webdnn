from webdnn.graph import node


class Attribute:
    base: "node.Node"

    def __init__(self, base: "node.Node"):
        self.base = base
