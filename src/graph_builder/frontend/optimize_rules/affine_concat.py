from typing import List

from graph_builder.graph import Operator, operators as O, Variable
from graph_builder.optimizer import OptimizeRule
from graph_builder.util import flags


class AffineConcat(OptimizeRule):
    """
    (Convolution2D|Linear)(AxiswiseScale|AxiswiseBias)+ という形式に対し、
    Scaleを(Convolution2D|Linear)のウェイトに統合し、Biasは最後に1つだけにする
    """

    def __call__(self, graph: Operator):
        if not flags.optimize.AFFINE_CONCAT:
            return graph, False

        flag_changed = False
        touched_operators = set()
        # 深さ優先探索で、深く進んでいくときに(AxiswiseScale|AxiswiseBias)が連続したのち
        # (Convolution2D|Linear)が見つかるパターンを探す
        # 1本道でなければダメ(途中から分岐して別用途に使われていたら最適化不可)

        found_seq = None
        print('affineconcat')
        print('outputs:' + str(graph.outputs))
        for output in graph.outputs.values():
            opr = output.output_from
            oprs = []
            if isinstance(opr, O.Compose):
                composed = opr  # type: O.Compose
                oprs = list(opr.outputs_alias)
            else:
                oprs = [opr]
            print('oprs: ' + str(oprs))
            for opr in oprs:
                found_seq = self._search(opr, touched_operators, [])
                if found_seq is not None:
                    break
            if found_seq is not None:
                break

        print('AffineConcat: found ' + str(found_seq))

        return graph, flag_changed

    def _search(self, target_operator, touched_operators, candidate_sequence):
        # 開始/継続条件: (AxiswiseScale|AxiswiseBias)であり、自分への入力が他で使われていないこと
        # 終了条件: (Convolution2D|Linear)であり、シーケンスにAxiswiseScaleが含まれること
        if target_operator in touched_operators:
            # 探索済みの部分にぶつかった
            return None
        print(target_operator)
        touched_operators.add(target_operator)
        if isinstance(target_operator, O.Convolution2D):
            # sequenceの終端になりうる
            if len(candidate_sequence) > 0 and any(isinstance(opr, O.AxiswiseScale) for opr in candidate_sequence):
                # 該当シーケンスが見つかった
                return candidate_sequence + [target_operator]
        if isinstance(target_operator, O.AxiswiseScale) or isinstance(target_operator, O.AxiswiseBias):
            input_var = target_operator.inputs["x"]
            if len(input_var.input_to) == 1:
                # 開始/継続条件を満たす
                print("start cond")
                return self._search(input_var.output_from, touched_operators, candidate_sequence + [target_operator])
        # 継続せず、深さ優先探索
        for input_var in target_operator.inputs.values():
            if input_var.output_from is not None:
                seq = self._search(input_var.output_from, touched_operators, [])
                if seq is not None:
                    return seq
        return None

