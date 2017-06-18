import re
from typing import List, Tuple


class Tag:
    def __init__(self, original: str, name: str, args: List[str], span: Tuple[int, int]):
        self.original = original
        self.name = name
        self.args = args
        self.span = span


_reg_tag = re.compile("%%([a-zA-Z0-9_]+)(?:\((.*?)\))?%%", re.MULTILINE)


class Injector:
    def inject_tag(self, tag: Tag) -> str:
        raise NotImplementedError

    def inject(self, text: str) -> str:
        tags = []
        pos = 0
        while True:
            ma = _reg_tag.search(text, pos)
            if ma is None:
                break

            original = ma.group(0)
            name = ma.group(1)
            args = [] if ma.group(2) is None else list(map(str.strip, ma.group(2).split(",")))
            span = ma.span()

            tag = Tag(original, name, args, span)
            tags.append(tag)
            pos = tag.span[1]

        for tag in sorted(tags, key=lambda x: x.span[1], reverse=True):
            text = text[:tag.span[0]] + self.inject_tag(tag) + text[tag.span[1]:]

        return text
