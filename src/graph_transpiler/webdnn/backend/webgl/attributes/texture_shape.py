from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.graph.attribute import Attribute
from webdnn.graph.variable import Variable
from webdnn.util import config


class TextureShape(Attribute):
    def __init__(self, base: Variable):
        if base.has_attribute(TextureShape):
            raise ValueError(f"\'TextureShape\' attribute has been already registered to {base}.")
        MAX_TEXTURE_SIZE = config.WEBGL_MAX_TEXTURE_SIZE
        super(TextureShape, self).__init__(base)
        spacial_size = base.size // ChannelMode.elements_per_pixel(base)
        self.width = MAX_TEXTURE_SIZE if spacial_size > MAX_TEXTURE_SIZE else spacial_size  # type: int
        self.height = (spacial_size + MAX_TEXTURE_SIZE - 1) // MAX_TEXTURE_SIZE if spacial_size > MAX_TEXTURE_SIZE else 1  # type: int

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
