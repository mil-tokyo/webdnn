import ast
from typing import Dict, Tuple, Union, List

from webdnn.graph.place_holder import PlaceHolder


class Shape:
    @staticmethod
    def parse(text: str) -> Tuple[List[Union[int, PlaceHolder]], Dict[str, PlaceHolder]]:
        tmp = ast.literal_eval(text)
        shape = []
        placeholders = {}
        for t in tmp:
            if isinstance(t, str):
                pt = PlaceHolder(label=t)
                placeholders[t] = pt

            elif isinstance(t, int):
                pt = t

            else:
                raise ValueError(f"Invalid shape format: '{text}'")

            shape.append(pt)

        return shape, placeholders
