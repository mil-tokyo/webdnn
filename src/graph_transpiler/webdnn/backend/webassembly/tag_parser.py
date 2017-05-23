import re
from typing import List, Tuple, NamedTuple

from typing import Match


class Tag(NamedTuple):
    original: str
    name: str
    args: List[str]
    span: Tuple[int, int]


reg_tag = re.compile("%%([a-zA-Z0-9_]+)(?:\((.*)\))?%%", re.MULTILINE)


class TagParser:
    @classmethod
    def parse(cls, text: str) -> List[Tag]:
        pos = 0
        result = []
        while True:
            ma = reg_tag.search(text, pos)  # type: Match
            if ma is None:
                break
            pos = ma.end()

            original = ma.group(0)
            name = ma.group(1)
            args = [] if ma.group(2) is None else list(map(str.strip, ma.group(2).split(",")))
            span = ma.span()

            # FIXME: This noinspection comment is not required. It's maybe a PyCharm's Bug?
            # noinspection PyArgumentList
            result.append(Tag(original, name, args, span))

        result.sort(key=lambda x: x.span[0], reverse=True)
        return result
