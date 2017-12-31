from typing import Dict, Tuple, Union, List

from webdnn.graph.placeholder import Placeholder


class Shape:
    @staticmethod
    def parse(text: str) -> Tuple[List[Union[int, Placeholder]], Dict[str, Placeholder]]: ...
