from typing import List

import numpy as np

from graph_builder.graph import traverse
from graph_builder.graph.axis import Axis
from graph_builder.graph.graph import Graph
from graph_builder.graph.operator import Operator
from graph_builder.graph.operators.axiswise_bias import AxiswiseBias
from graph_builder.graph.operators.axiswise_scale import AxiswiseScale
from graph_builder.graph.operators.convolution2d import Convolution2D
from graph_builder.graph.optimize_rule import OptimizeRule
from graph_builder.graph.variables.attributes.order import OrderC
from graph_builder.graph.variables.constant_variable import ConstantVariable
from graph_builder.util import flags


class ConcatAffine(OptimizeRule):
    """
    (Convolution2D|Linear)(AxiswiseScale|AxiswiseBias)+ という形式に対し、
    Scaleを(Convolution2D|Linear)のウェイトに統合し、Biasは最後に1つだけにする
    """

    def optimize(self, graph: Graph):
        if not flags.optimize.CONCAT_AFFINE:
            return graph, False

        flag_changed = False

        while True:
            flag_changed_in_iter = False
            ops = traverse.listup_operators(graph)
            current_seq = []
            for op in ops:
                if isinstance(op, Convolution2D):
                    self._start_found(op, current_seq)
                elif (isinstance(op, AxiswiseScale) or isinstance(op, AxiswiseBias)) and \
                        op.parameters["axis"] is Axis.C:
                    self._cont_found(op, current_seq)
                else:
                    flag_changed_in_iter = self._non_cont_found(current_seq)
                if flag_changed_in_iter:
                    break

            flag_changed |= flag_changed_in_iter
            if not flag_changed_in_iter:
                break

        return graph, flag_changed

    def _start_found(self, op: Operator, current_seq: List[Operator]):
        # シーケンスの開始条件が発生
        if len(current_seq) > 0:
            # end of last sequence
            self._non_cont_found(current_seq)
            current_seq.clear()
        current_seq.append(op)

    # noinspection PyMethodMayBeStatic
    def _cont_found(self, op: Operator, current_seq: List[Operator]):
        # シーケンスの継続条件が発生
        if len(current_seq) > 0:
            current_seq.append(op)

    def _non_cont_found(self, current_seq: List[Operator]):
        # シーケンスに含まれない要素が発生
        if len(current_seq) > 0:
            # check if sequence can be converted
            if self._check_sequence(current_seq):
                # グラフ圧縮の実行
                self._compress_sequence(current_seq)
                return True
            current_seq.clear()
        return False

    # noinspection PyMethodMayBeStatic
    def _check_sequence(self, seq: List[Operator]):
        # 実際にマージ可能かをチェックする
        # シーケンス内で受け渡される変数が分岐しないことをチェック(1本道)
        for i in range(len(seq)):
            op = seq[i]
            if len(op.outputs) != 1:
                return False
            out_var = op.outputs["y"]
            if i < len(seq) - 1:
                if len(out_var.input_to) != 1:
                    return False
                if list(out_var.input_to)[0] is not seq[i + 1]:
                    return False

        # Scale*1以上またはBias*2以上があること
        scale_count = 0
        bias_count = 0
        for op in seq:
            if isinstance(op, AxiswiseScale):
                scale_count += 1
            if isinstance(op, AxiswiseBias):
                bias_count += 1
        if scale_count <= 0 and bias_count <= 1:
            return False

        return True

    def _compress_sequence(self, seq: List[Operator]):
        # Convolution2D|LinearとAxiswiseBiasだけに変更する
        conv_op = seq[0]
        conv_out = conv_op.outputs["y"]
        n_channels = conv_out.shape_dict[Axis.C]

        # scale, biasの集計
        merged_scale = np.ones((n_channels,), dtype=np.float32)
        merged_bias = np.zeros((n_channels,), dtype=np.float32)
        for op in seq[1:]:
            if isinstance(op, AxiswiseScale):
                weight_var = op.inputs["s"]
                merged_scale *= weight_var.data
                merged_bias *= weight_var.data
            elif isinstance(op, AxiswiseBias):
                weight_var = op.inputs["b"]
                merged_bias += weight_var.data
            else:
                raise NotImplementedError()

        # Conv/Linearの出力チャンネル(N)にscaleをかける
        conv_weight_var = conv_op.inputs["w"]
        out_channel_pos = conv_weight_var.axis_order.axes_dict[Axis.N]
        broadcast = [None] * conv_weight_var.axis_order.ndim
        broadcast[out_channel_pos] = slice(None)
        # HWNCなら、broadcast==[None, None, :, None]
        conv_weight_var.data *= merged_scale[broadcast]

        # Scale/Biasレイヤーを削除して、新しいBiasレイヤーを元々の出力につなぐ
        final_out = seq[-1].outputs["y"]
        for op in seq[1:]:
            op.remove_all()
        const_bias = ConstantVariable(merged_bias, OrderC)
        bias_op = AxiswiseBias(conv_op.name + "_tail_bias", axis=Axis.C)
        bias_op.append_input("x", conv_out)
        bias_op.append_input("b", const_bias)
        bias_op.append_output("y", final_out)
