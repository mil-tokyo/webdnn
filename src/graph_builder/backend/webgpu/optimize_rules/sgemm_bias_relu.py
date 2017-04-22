from graph_builder.backend.webgpu.kernels import sgemm_bias_relu
from graph_builder.backend.webgpu.kernels.sgemm_bias_relu import sgemm_bias_relu
from graph_builder.backend.webgpu.operators.sgemm import Sgemm
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.relu import Relu
from graph_builder.optimizer import util
from graph_builder.optimizer.optimize_rule import OptimizeRule


class SgemmBiasRelu(OptimizeRule):
    """
    sgemm + bias + reluをひとまとめにする
    """

    def __call__(self, graph: Operator):
        flag_changed = False

        for match in util.search_sub_structure(graph, [Sgemm, AxiswiseBias, Relu]):
            sgemm: Sgemm = match[0]
            axiswise_bias: AxiswiseBias = match[1]
            relu: Relu = match[2]

            x = sgemm.inputs["x"]
            w = sgemm.inputs["w"]
            b = axiswise_bias.inputs["b"]
            y = relu.outputs["y"]

            sgemm.remove_all()
            axiswise_bias.remove_all()
            relu.remove_all()

            op = Operator("sgemm_bias_relu")
            op.append_input("x", x)
            op.append_input("w", w)
            op.append_input("b", b)
            op.append_output("y", y)
            op.parameters["custom_kernel"] = sgemm_bias_relu

            flag_changed = True

        return graph, flag_changed
