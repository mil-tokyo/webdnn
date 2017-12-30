from webdnn.graph.attribute import Attribute
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util import config


class TextureShape(Attribute):
    def __init__(self, variable: Variable):
        MAX_TEXTURE_SIZE = config.WEBGL_MAX_TEXTURE_SIZE

        spacial_size = variable.size
        if Placeholder.check_resolved(variable.size):
            self.width = MAX_TEXTURE_SIZE if spacial_size > MAX_TEXTURE_SIZE else spacial_size  # type: int
            self.height = (spacial_size + MAX_TEXTURE_SIZE - 1) // MAX_TEXTURE_SIZE if spacial_size > MAX_TEXTURE_SIZE else 1  # type: int

        else:
            self.width = MAX_TEXTURE_SIZE
            self.height = (variable.size + MAX_TEXTURE_SIZE - 1) // MAX_TEXTURE_SIZE

    def __str__(self):
        return f"TextureShape[{self.height}, {self.width}]"

    @staticmethod
    def set(variable: Variable, width: int, height: int):
        if variable.has_attribute(TextureShape):
            attribute = variable.get_attribute(TextureShape)[0]
        else:
            attribute = TextureShape(variable)
            variable.attributes.add(attribute)

        attribute.width = width
        attribute.height = height

    @staticmethod
    def get(variable: Variable):
        if variable.has_attribute(TextureShape):
            attribute = variable.get_attribute(TextureShape)[0]

        else:
            attribute = TextureShape(variable)
            variable.attributes.add(attribute)

        return attribute.height, attribute.width
