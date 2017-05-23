# from typing import Dict, List
#
# from webdnn.graph.operator import Operator
# from webdnn.graph.operators.attributes.inplace import Inplace
# from webdnn.graph.operators.attributes.post_axiswise import PostAxiswise
# from webdnn.graph.operators.attributes.post_elementwise import PostElementwise
# from webdnn.graph.variable import Variable
#
#
# class Reshape(Operator):
#     """
#     入力変数の形を変形するレイヤー
#     形状変化を表現する便宜上のもので、データ操作はない
#     """
#     attributes = {PostElementwise,
#                   PostAxiswise,
#                   Inplace}
#
#     def __init__(self, name: str, parameters: Dict[str, object]):
#         """
#         parameters: {out_shape: Tuple, out_order: Order}
#         :param name:
#         :param parameters:
#         """
#         raise NotImplementedError()  # 入力オーダーの定義がなく、中途半端なので使い方を決めてから再実装
#         assert "out_shape" in parameters
#         assert "out_order" in parameters
#         assert issubclass(type(parameters["out_order"]), AxisOrder)
#         super().__init__(name, parameters)
#
#     def __call__(self, x: Variable):
#         """
#         Args:
#             x (:class:`~webdnn.graph.variable.Variable`): Input
#
#         Returns:
#             tuple of :class:`~webdnn.graph.variable.Variable`: Output
#         """
#         out_shape = self.parameters["out_shape"]  # type: List[int]
#         y = Variable(out_shape, self.parameters["out_order"])
#         self.append_input("x", x)
#         self.append_output("y", y)
#         return y,
