from typing import Optional, Iterable, Union

import numpy as np

from webdnn.graph.operator import Operator
from webdnn.graph.order import Order
from webdnn.graph.place_holder import PlaceHolder
from webdnn.graph.variable import Variable


class Sgemm(Operator):
    def __init__(self, name: Optional[str], M: Union[int, PlaceHolder], N: Union[int, PlaceHolder], K: Union[int, PlaceHolder],
                 out_shape: Iterable[PlaceHolder], out_order: Order, transpose_A: bool, transpose_B: bool):
        super().__init__(name)

        # NOTE: out_shapeをIterableではなくCollectionにすればこれは解決する
        #       しかしPyCharmでは issubclass(List[int], Collection[int]) がTrueにならない（バグ？）ため、
        #       やむを得ずこのようにしている
        #
        # noinspection PyTypeChecker
        assert len(out_shape) == out_order.ndim
        assert np.product(out_shape) == M * N

        self.parameters["M"] = M
        self.parameters["N"] = N
        self.parameters["K"] = K
        self.parameters["out_shape"] = out_shape
        self.parameters["out_order"] = out_order
        self.parameters["transpose_A"] = transpose_A
        self.parameters["transpose_B"] = transpose_B

    def __call__(self, A: Variable, B: Variable):
        assert A.size == self.M * self.K
        assert B.size == self.N * self.K

        self.append_input("A", A)
        self.append_input("B", B)

        C = Variable(
            self.parameters["out_shape"],
            self.parameters["out_order"]
        )
        self.append_output("C", C)

        return C,

    @property
    def M(self) -> Union[int, PlaceHolder]:
        return self.parameters["M"]

    @property
    def N(self) -> Union[int, PlaceHolder]:
        return self.parameters["N"]

    @property
    def K(self) -> Union[int, PlaceHolder]:
        return self.parameters["K"]

    @property
    def transpose_A(self) -> bool:
        return self.parameters["transpose_A"]

    @property
    def transpose_B(self) -> bool:
        return self.parameters["transpose_B"]
