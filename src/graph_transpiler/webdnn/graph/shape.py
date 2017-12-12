import ast
from typing import Dict, Tuple, Union, List

from webdnn.graph.placeholder import Placeholder
import re

_reg_quote = re.compile("['\"]")
_reg_trail_space = re.compile("\s{2,}")
_reg_placeholder = re.compile("[a-zA-Z_]+")


def _normalize_text(text: str) -> str:
    text = _reg_quote.sub(lambda ma: " ", text)
    text = _reg_trail_space.sub(lambda ma: " ", text)
    text = _reg_placeholder.sub(lambda ma: f"'{ma[0]}'", text)
    return text


class Shape:
    @staticmethod
    def parse(text: str) -> Tuple[List[Union[int, Placeholder]], Dict[str, Placeholder]]:
        """
        Parse string and return shape

        Args:
            text: string to specify shape

        Returns:
            shape: parsed shape
            placeholders: parsed placeholders
        """
        normalized_text = _normalize_text(text)
        tmp = ast.literal_eval(normalized_text)
        shape = []
        placeholders = {}
        for i, t in enumerate(tmp):
            if isinstance(t, str):
                pt = Placeholder(label=t)
                placeholders[t] = pt

            elif isinstance(t, int):
                pt = t

            else:
                raise ValueError("[Shape.parse()] Invalid shape format. Each element of shape must be int or str:"
                                 f"text='{text}', "
                                 f"{normalized_text + ', ' if normalized_text != text else ''}"
                                 f"type(shape[{i}])={type(t)}")

            shape.append(pt)

        return shape, placeholders
