from typing import Callable

from webdnn.backend.code_generator.injector import Injector, Tag
from webdnn.graph import traverse
from webdnn.graph.attribute import Attribute
from webdnn.graph.node import Node
from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.inplace import Inplace

_noop = lambda exp: exp


class InlineInplace(Attribute):
    injector: Callable[[str], str]
    inplace: Inplace

    def __init__(self, base: Node, injector: Callable[[str], str], inplace: Inplace):
        super(InlineInplace, self).__init__(base)
        self.injector = injector
        self.inplace = inplace

    def get_input(self):
        return self.inplace.get_input()

    def get_output(self):
        return self.inplace.get_output()


class PostInlineInplace(Attribute):
    injected: InlineInplace = None

    def register_injected(self, attr: InlineInplace):
        self.injected = attr


class InlineInjector(Injector):
    def __init__(self, op: Operator):
        self.delegate = lambda exp: exp  # type: Callable[[str], str]
        self.has_inline = traverse.check_attribute_match(op, PostInlineInplace)

        if self.has_inline:
            post_inline_inplace = op.get_attribute(PostInlineInplace)[0]  # type: PostInlineInplace
            if post_inline_inplace.injected is not None:
                self.delegate = post_inline_inplace.injected.injector

    def inject_tag(self, tag: Tag):
        if tag.name == "INLINE":
            return self.delegate(tag.args[0])

        else:
            return tag.original
