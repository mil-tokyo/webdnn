# -*- coding:utf-8 -*-

"""
Chainer Link -> Graph object converters
Assuming Chainer 1.23
"""

from typing import Dict, Set, List, Iterable, Type
import numpy as np
import chainer
import chainer.computational_graph
import chainer.functions as F
from graph_builder.graph import operators as O
from graph_builder.graph.graph import Variable, Node, Operator
import graph_builder.graph.operators as operators
from graph_builder.graph import Attribute
from graph_builder.graph.operators import attributes as A
import graph_builder.graph.variables.attributes as VA
from graph_builder.graph.variables.constant import Constant

unique_ctr = 0


def generate_unique_name(prefix):
    global unique_ctr
    unique_ctr += 1
    return prefix + str(unique_ctr)


class OperatorBlock:
    # Chainerで1つのFunctionが2つのレイヤーに分解されたときに、その間をつなぐために生成されたVariable
    hidden_vars: List[Variable]
    # 元々のウェイトを扱いやすく変換したConstantを作成した場合に登録
    hidden_consts: List[Constant]

    def __init__(self):
        self.hidden_vars = []
        self.hidden_consts = []

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        raise NotImplementedError()


class ReluBlock(OperatorBlock):
    cfunc: chainer.functions.ReLU

    def __init__(self, cfunc: chainer.functions.ReLU):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        assert len(inputs) == 1
        opr = operators.Relu(generate_unique_name(self.cfunc.label), {})
        return opr(inputs[0])


class LinearBlock(OperatorBlock):
    cfunc: chainer.functions.connection.linear.LinearFunction

    def __init__(self, cfunc: chainer.functions.Linear):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        linear_opr = operators.Linear(generate_unique_name(self.cfunc.label), {})
        x = inputs[0]
        w = inputs[1]
        if x.ndim == 4 and w.ndim == 2:
            # wを4次元に拡張 (NC -> NCHW)
            x_shape_dict = x.shape_dict
            w_shape_dict = w.shape_dict
            assert x_shape_dict[A.Axis.C] * x_shape_dict[A.Axis.H] * x_shape_dict[A.Axis.W] == w_shape_dict[A.Axis.C]
            assert w.axis_order is VA.OrderNC
            w.attributes.remove(VA.OrderNC)
            w.attributes.add(VA.OrderNCHW)
            w.axis_order = VA.OrderNCHW
            w_new_shape = [w_shape_dict[A.Axis.N], x_shape_dict[A.Axis.C], x_shape_dict[A.Axis.H],
                           x_shape_dict[A.Axis.W]]
            w.shape = w_new_shape
            w.data = w.data.reshape(w_new_shape)

        opr_out, = linear_opr(inputs[0], inputs[1])
        if len(inputs) == 3:
            # biasあり
            bias_opr = operators.AxiswiseBias(generate_unique_name(self.cfunc.label), {"axis": A.Axis.C})
            self.hidden_vars.append(opr_out)
            opr_out, = bias_opr(opr_out, inputs[2])
        return [opr_out]


class Convolution2DBlock(OperatorBlock):
    cfunc: chainer.functions.connection.convolution_2d.Convolution2DFunction

    def __init__(self, cfunc: chainer.functions.connection.convolution_2d.Convolution2DFunction):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        x = inputs[0]
        w = inputs[1]
        w_shape_dict = w.shape_dict
        conv_opr = operators.Convolution2D(generate_unique_name(self.cfunc.label),
                                           {"ksize": (w_shape_dict[A.Axis.H], w_shape_dict[A.Axis.W]),
                                            "stride": (self.cfunc.sy, self.cfunc.sx),
                                            "padding": (self.cfunc.ph, self.cfunc.pw)})

        opr_out, = conv_opr(inputs[0], inputs[1])
        if len(inputs) == 3:
            # biasあり
            bias_opr = operators.AxiswiseBias(generate_unique_name(self.cfunc.label), {"axis": A.Axis.C})
            self.hidden_vars.append(opr_out)
            opr_out, = bias_opr(opr_out, inputs[2])
        return [opr_out]


class MaxPooling2DBlock(OperatorBlock):
    cfunc: chainer.functions.pooling.max_pooling_2d.MaxPooling2D

    def __init__(self, cfunc: chainer.functions.pooling.max_pooling_2d.MaxPooling2D):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        x = inputs[0]
        conv_opr = operators.MaxPooling2D(generate_unique_name(self.cfunc.label),
                                          {"ksize": (self.cfunc.kh, self.cfunc.kw),
                                           "stride": (self.cfunc.sy, self.cfunc.sx),
                                           "padding": (self.cfunc.ph, self.cfunc.pw)})

        opr_out, = conv_opr(inputs[0])
        return [opr_out]


class AveragePooling2DBlock(OperatorBlock):
    cfunc: chainer.functions.pooling.average_pooling_2d.AveragePooling2D

    def __init__(self, cfunc: chainer.functions.pooling.average_pooling_2d.AveragePooling2D):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        x = inputs[0]
        conv_opr = operators.AveragePooling2D(generate_unique_name(self.cfunc.label),
                                              {"ksize": (self.cfunc.kh, self.cfunc.kw),
                                               "stride": (self.cfunc.sy, self.cfunc.sx),
                                               "padding": (self.cfunc.ph, self.cfunc.pw)})

        opr_out, = conv_opr(inputs[0])
        return [opr_out]


class BatchNormalizationBlock(OperatorBlock):
    cfunc: chainer.functions.normalization.batch_normalization.BatchNormalizationFunction

    def __init__(self, cfunc: chainer.functions.normalization.batch_normalization.BatchNormalizationFunction):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        assert len(inputs) == 5
        x, gamma, beta, mean, variance = inputs
        # x以外の変数は、加工して新しいConstantとして使う
        # (x - mean) / sqrt(var + eps) * gamma + beta
        # gamma_div_std = gamma / sqrt(var + eps)
        # beta_scaled = beta - mean * gamma_div_std
        # y = x * gamma_div_std + beta_scaled
        gamma_div_std = gamma.data / np.sqrt(variance.data + self.cfunc.eps)
        beta_scaled = beta.data - mean.data * gamma_div_std

        scale_opr = operators.AxiswiseScale(generate_unique_name(self.cfunc.label), {"axis": A.Axis.C})
        gamma_div_std_const = Constant(gamma_div_std, VA.OrderC)
        scale_out, = scale_opr(x, gamma_div_std_const)
        self.hidden_vars.append(scale_out)
        self.hidden_consts.append(gamma_div_std_const)

        offset_opr = operators.AxiswiseBias(generate_unique_name(self.cfunc.label), {"axis": A.Axis.C})
        beta_scaled_const = Constant(beta_scaled, VA.OrderC)
        offset_out, = offset_opr(scale_out, beta_scaled_const)
        self.hidden_consts.append(beta_scaled_const)

        return [offset_out]


class AddBlock(OperatorBlock):
    cfunc: chainer.functions.math.basic_math.Add

    def __init__(self, cfunc: chainer.functions.math.basic_math.Add):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        opr = operators.ElementwiseSum(generate_unique_name(self.cfunc.label), {})
        return list(opr(*inputs))


class ReshapeBlock(OperatorBlock):
    # Currently, only removing HW axis is allowed
    # NCHW (n,c,h,w) => NC (n,c*h*w) (assuming c-order)
    cfunc: chainer.functions.array.reshape.Reshape

    def __init__(self, cfunc: chainer.functions.array.reshape.Reshape):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        assert len(inputs) == 1
        input = inputs[0]
        # NCHWをNCにする場合のみ想定
        assert input.axis_order is VA.OrderNCHW
        assert len(self.cfunc.shape) == 2
        assert self.cfunc.shape[0] == input.shape[0]  # Nは変化しない

        opr = operators.Flatten(generate_unique_name(self.cfunc.label),
                                {"in_axes": [A.Axis.C, A.Axis.H, A.Axis.W], "out_axes": [A.Axis.C]})
        return list(opr(input))


BLOCK_CLASSES = [(chainer.functions.ReLU, ReluBlock),
                 (chainer.functions.connection.linear.LinearFunction, LinearBlock),
                 (chainer.functions.connection.convolution_2d.Convolution2DFunction, Convolution2DBlock),
                 (chainer.functions.pooling.max_pooling_2d.MaxPooling2D, MaxPooling2DBlock),
                 (chainer.functions.pooling.average_pooling_2d.AveragePooling2D, AveragePooling2DBlock),
                 (chainer.functions.normalization.batch_normalization.BatchNormalizationFunction,
                  BatchNormalizationBlock),
                 (chainer.functions.math.basic_math.Add, AddBlock),
                 (chainer.functions.array.reshape.Reshape, ReshapeBlock)]


class ChainerGraphConverter:
    def __init__(self):
        self._cvar_to_nvar = {}  # id(chainer.Variable) => Variable (note: chainerに対応しないVariableも作られる)
        self._cvar_ids = []  # id(chainer.Variable)
        self._known_nvars = []  # 存在するVariable(include Constant)

    def convert(self, chainer_computational_graph: chainer.computational_graph.ComputationalGraph,
                input_vars: List[chainer.Variable], output_vars: List[chainer.Variable]) -> Node:
        # 戦略
        # 生成済み変数(chainer.Variable)をセットに入れる; 入力変数およびウェイト
        # 生成済み変数だけを入力とし、未処理のchainer.Functionを変換し、生成済み変数セットに追加
        # 未処理のchainer.Functionがなくなったら終わり
        self._cvar_to_nvar = {}
        self._cvar_ids = []
        self._known_nvars = []
        self._convert_weight_vars(chainer_computational_graph)
        self._convert_input_vars(input_vars)

        pending_functions = [cfunc for cfunc in chainer_computational_graph.nodes if
                             isinstance(cfunc, chainer.Function)]
        while len(pending_functions) > 0:
            for cfunc in pending_functions:
                if all(((id(cvar) in self._cvar_ids) for cvar in cfunc.inputs)):
                    # このレイヤーは入力が揃った
                    opr_block = self._construct_operator_block(cfunc)
                    out_nvars = opr_block([self._cvar_to_nvar[id(cvar)] for cvar in cfunc.inputs])
                    assert len(out_nvars) == len(cfunc.outputs), str(cfunc)
                    self._known_nvars.extend(opr_block.hidden_consts)
                    self._known_nvars.extend(opr_block.hidden_vars)
                    # 出力変数を対応づける
                    for out_nvar, out_cvar_wref in zip(out_nvars, cfunc.outputs):
                        out_cvar = out_cvar_wref()
                        assert tuple(out_nvar.shape) == out_cvar.shape, str(cfunc)
                        self._cvar_to_nvar[id(out_cvar)] = out_nvar
                        self._cvar_ids.append(id(out_cvar))
                        self._known_nvars.append(out_nvar)
                    pending_functions.remove(cfunc)
                    break  # for cfunc in pending_functions
            else:
                print(pending_functions)
                raise ValueError("inputs to functions cannot be resolved.")

        # 出力変数にAttributeをつける
        for cvar in output_vars:
            if id(cvar) not in self._cvar_ids:
                raise ValueError("Output variable is not generated by graph.")
            nvar = self._cvar_to_nvar[id(cvar)]
            nvar.attributes.add(VA.Output)

        # このフレームワークで標準的なデータオーダーに変更
        self._transpose_vars(self._known_nvars)

        graph = O.Compose.compose_with_vars("graph",
                                            [self._cvar_to_nvar[id(cvar)] for cvar in input_vars],
                                            [self._cvar_to_nvar[id(cvar)] for cvar in output_vars])
        return graph

    def _convert_input_vars(self, input_vars: Iterable[chainer.Variable]):
        for cvar in input_vars:
            self._convert_var(cvar, attrs={VA.Input})

    def _convert_weight_vars(self, chainer_computational_graph: chainer.computational_graph.ComputationalGraph):
        # 名前付きの変数を変換
        for cvar in chainer_computational_graph.nodes:
            if isinstance(cvar, chainer.Variable):
                if cvar.name is not None:
                    self._convert_var(cvar)
            elif isinstance(cvar, chainer.functions.normalization.batch_normalization.BatchNormalizationFunction):
                # BNのmean, varは名無しだがウェイト
                assert len(cvar.inputs) == 5  # data, gamma, bias, mean, var
                self._convert_var(cvar.inputs[3], force_constant=True)
                self._convert_var(cvar.inputs[4], force_constant=True)

    def _convert_var(self, cvar: chainer.Variable, attrs: Iterable[Type[Attribute]] = None, force_constant=False):
        assert id(cvar) not in self._cvar_ids
        ndim = len(cvar.shape)
        if ndim == 4:
            # both weight and variable
            order = VA.OrderNCHW
        elif ndim == 2:
            # both weight and variable
            order = VA.OrderNC
        elif ndim == 1:
            # both weight and variable
            order = VA.OrderC
        else:
            raise NotImplementedError()

        if cvar.name is not None or force_constant:
            nvar = Constant(chainer.cuda.to_cpu(cvar.data), order)  # force on CPU
        else:
            nvar = Variable(cvar.shape, order)
        if attrs is not None:
            nvar.attributes.update(attrs)

        self._cvar_to_nvar[id(cvar)] = nvar
        self._cvar_ids.append(id(cvar))
        self._known_nvars.append(nvar)
        return nvar

    def _construct_operator_block(self, cfunc: chainer.Function) -> OperatorBlock:
        for function_class, block_class in BLOCK_CLASSES:
            if isinstance(cfunc, function_class):
                return block_class(cfunc)
        raise ValueError("Unknown layer {}".format(type(cfunc)))

    def _transpose_vars(self, nvars: Iterable[Variable]):
        """
        変数を、標準的なAxisOrderに変更
        :param nvars: 
        :return: 
        """
        for nvar in nvars:
            if isinstance(nvar, Constant):
                if nvar.ndim == 1:
                    nvar.change_axis_order(VA.OrderC)
                elif nvar.ndim == 2:
                    nvar.change_axis_order(VA.OrderCN)
                elif nvar.ndim == 4:
                    assert len(nvar.input_to) == 1
                    first_input_to = list(nvar.input_to)[0]
                    if isinstance(first_input_to, operators.Convolution2D):
                        nvar.change_axis_order(VA.OrderHWNC)
                    elif isinstance(first_input_to, operators.Linear):
                        nvar.change_axis_order(VA.OrderHWCN)
                    else:
                        # 今の所ないはず
                        raise ValueError()
            else:
                if nvar.ndim == 1:
                    nvar.change_axis_order(VA.OrderC)
                elif nvar.ndim == 2:
                    nvar.change_axis_order(VA.OrderNC)
                elif nvar.ndim == 4:
                    nvar.change_axis_order(VA.OrderNHWC)
