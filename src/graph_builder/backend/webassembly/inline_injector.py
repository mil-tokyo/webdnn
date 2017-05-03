from typing import Callable

from graph_builder.backend.webassembly.tag_parser import TagParser


class InlineInjector:
    delegate: Callable[[str], str]

    def __init__(self):
        self.delegate = lambda exp: exp

    def inject(self, source: str) -> str:
        for tag in TagParser.parse(source):
            if tag.name == "INLINE":
                source = source[:tag.span[0]] + self.delegate(tag.args[0]) + source[tag.span[1]:]

        return source
