from webdnn.graph.attribute import Attribute
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util import config


class TextureShape(Attribute[Variable]):
    def __init__(self, base: Variable):
        if base.has_attribute(TextureShape):
            raise ValueError(f"\'TextureShape\' attribute has been already registered to {base}.")
        MAX_TEXTURE_SIZE = config.WEBGL_MAX_TEXTURE_SIZE
        super(TextureShape, self).__init__(base)
        spacial_size = base.size
        if Placeholder.check_resolved(base.size):
            self.width = MAX_TEXTURE_SIZE if spacial_size > MAX_TEXTURE_SIZE else spacial_size  # type: int
            self.height = (spacial_size + MAX_TEXTURE_SIZE - 1) // MAX_TEXTURE_SIZE if spacial_size > MAX_TEXTURE_SIZE else 1  # type: int

        else:
            self.width = MAX_TEXTURE_SIZE
            self.height = (base.size + MAX_TEXTURE_SIZE - 1) // MAX_TEXTURE_SIZE

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
        if base.has_attribute(TextureShape):
            attribute = base.get_attribute(TextureShape)[0]
        else:
            attribute = TextureShape(base)
            base.attributes.add(attribute)

        return attribute.height, attribute.width
