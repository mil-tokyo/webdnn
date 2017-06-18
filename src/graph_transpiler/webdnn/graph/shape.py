import ast
from typing import Dict, Tuple, Union, List

from webdnn.graph.placeholder import Placeholder


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
        tmp = ast.literal_eval(text)
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
                                 f"text='{text}', type(shape[{i}])={type(t)}")

            shape.append(pt)

        return shape, placeholders
