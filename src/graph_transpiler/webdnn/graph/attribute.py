from webdnn.graph import node


class Attribute:
    def __init__(self, base: "node.Node"):
        self.base = base  # type: node.Node

    def __str__(self):
        return self.__class__.__name__

    @classmethod
    def set(cls, base: "node.Node", kwargs):
        base.attributes.add(cls(base=base, **kwargs))
