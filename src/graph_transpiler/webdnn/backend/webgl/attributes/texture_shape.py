from webdnn.graph.attribute import Attribute
from webdnn.graph.variable import Variable


class TextureShape(Attribute):
    def __init__(self, base: Variable):
        if base.has_attribute(TextureShape):
            raise ValueError(f"\'TextureShape\' attribute has been already registered to {base}.")

        super(TextureShape, self).__init__(base)
        self.width = 2048 if base.size > 2048 else base.size  # type: int
        self.height = (base.size + 2048 - 1) // 2048 if base.size > 2048 else 1  # type: int

    def __str__(self):
        return f"TextureShape[{self.height}, {self.width}]"

    @staticmethod
    def set(base: Variable, width: int, height: int):
        if not base.has_attribute(TextureShape):
            attribute = TextureShape(base)
            base.attributes.add(attribute)
        else:
            attribute = base.get_attribute(TextureShape)[0]

        attribute.width = width
        attribute.height = height

    @staticmethod
    def get(base: Variable):
        if not base.has_attribute(TextureShape):
            attribute = TextureShape(base)
            base.attributes.add(attribute)
        else:
            attribute = base.get_attribute(TextureShape)[0]

        return [attribute.height, attribute.width]
