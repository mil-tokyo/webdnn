import hashlib
from typing import Union

from webdnn.backend.code_generator.injector import Tag, Injector
from webdnn.graph.operator import Operator


def _add_canonical_suffix(base_name: str, source: str):
    return


class KernelNameInjector(Injector):
    def __init__(self, base_name: Union[str, Operator]):
        self.base_name = base_name.__class__.__name__.lower() if isinstance(base_name, Operator) else base_name
        self.name = base_name

    def inject(self, text: str) -> str:
        self._text = text
        return super(KernelNameInjector, self).inject(text)

    def inject_tag(self, tag: Tag):
        if tag.name == "FUNC_NAME":
            self.name = f"{self.base_name}_{hashlib.sha224(self._text.encode('utf-8')).hexdigest()}"
            return self.name

        else:
            return tag.original
