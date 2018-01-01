from typing import Optional, Union, Sequence

from webdnn.graph.operator import Operator
from webdnn.graph.operators.attributes.associative import Associative
from webdnn.graph.order import Order
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul


class Sgemm(Operator):
    def __init__(self, name: Optional[str], M: Union[int, Placeholder], N: Union[int, Placeholder],
                 K: Union[int, Placeholder],
                 out_shape: Sequence[Union[int, Placeholder]], out_order: Order, transpose_A: bool, transpose_B: bool):
        super().__init__(name)

        assert len(out_shape) == out_order.ndim
        if Placeholder.check_resolved(mul(out_shape)) and Placeholder.check_resolved(M * N):
            assert mul(out_shape) == M * N

        self.parameters["M"] = M
        self.parameters["N"] = N
        self.parameters["K"] = K
        self.parameters["out_shape"] = out_shape
        self.parameters["out_order"] = out_order
        self.parameters["transpose_A"] = transpose_A
        self.parameters["transpose_B"] = transpose_B
        self.attributes.add(Associative(self, ('A', 'B')))

    def __call__(self, A: Variable, B: Variable):
        if Placeholder.check_resolved(A.size) and Placeholder.check_resolved(self.M * self.K):
            assert A.size == self.M * self.K
        if Placeholder.check_resolved(B.size) and Placeholder.check_resolved(self.N * self.K):
            assert B.size == self.N * self.K

        C = Variable(self.parameters["out_shape"], self.parameters["out_order"])

        self.append_input("A", A)
        self.append_input("B", B)
        self.append_output("C", C)
        return C,

    @property
    def M(self) -> Union[int, Placeholder]:
        return self.parameters["M"]

    @property
    def N(self) -> Union[int, Placeholder]:
        return self.parameters["N"]

    @property
    def K(self) -> Union[int, Placeholder]:
        return self.parameters["K"]

    @property
    def transpose_A(self) -> bool:
        return self.parameters["transpose_A"]

    @property
    def transpose_B(self) -> bool:
        return self.parameters["transpose_B"]
