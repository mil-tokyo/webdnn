# -*- coding:utf-8 -*-

"""
Chainer Link -> Graph object converters
Assuming Chainer 1.23 or 2.0
"""

from typing import List, Tuple

import chainer
import chainer.computational_graph
import numpy as np

from webdnn.graph.axis import Axis
from webdnn.graph.graph import Graph
from webdnn.graph.operators.average_pooling_2d import AveragePooling2D
from webdnn.graph.operators.axiswise_bias import AxiswiseBias
from webdnn.graph.operators.axiswise_scale import AxiswiseScale
from webdnn.graph.operators.convolution2d import Convolution2D
from webdnn.graph.operators.deconvolution2d import Deconvolution2D
from webdnn.graph.operators.elementwise_sum import ElementwiseSum
from webdnn.graph.operators.elu import Elu
from webdnn.graph.operators.flatten import Flatten
from webdnn.graph.operators.linear import Linear
from webdnn.graph.operators.local_response_normalization import LocalResponseNormalization
from webdnn.graph.operators.max_pooling_2d import MaxPooling2D
from webdnn.graph.operators.relu import Relu
from webdnn.graph.operators.scalar_affine import ScalarAffine
from webdnn.graph.operators.tanh import Tanh
from webdnn.graph.order import OrderNC, OrderNCHW, OrderC, OrderCN, OrderHWNC, OrderHWCN, \
    OrderNHWC, OrderCNHW, \
    Order
from webdnn.graph.variable import Variable
from webdnn.graph.variables.attributes.input import Input
from webdnn.graph.variables.attributes.output import Output
from webdnn.graph.variables.constant_variable import ConstantVariable

if chainer.__version__ >= "2.":
    chainer_v2 = True
    VariableNode = chainer.variable.VariableNode
else:
    chainer_v2 = False
    VariableNode = chainer.variable.Variable

unique_ctr = 0


def generate_unique_name(prefix):
    global unique_ctr
    unique_ctr += 1
    return prefix + str(unique_ctr)


class OperatorBlock:
    # Chainerで1つのFunctionが2つのレイヤーに分解されたときに、その間をつなぐために生成されたVariable
    hidden_vars: List[Variable]
    # 元々のウェイトを扱いやすく変換したConstantを作成した場合に登録
    hidden_consts: List[ConstantVariable]

    def __init__(self):
        self.hidden_vars = []
        self.hidden_consts = []

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        raise NotImplementedError()


class ReluBlock(OperatorBlock):
    cfunc: chainer.functions.ReLU

    def __init__(self, cfunc: chainer.functions.ReLU):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        assert len(inputs) == 1
        opr = Relu(generate_unique_name(self.cfunc.label))
        return opr(inputs[0])


class EluBlock(OperatorBlock):
    cfunc: chainer.functions.ELU

    def __init__(self, cfunc: chainer.functions.ELU):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        assert len(inputs) == 1
        opr = Elu(generate_unique_name(self.cfunc.label))
        return opr(inputs[0])


class TanhBlock(OperatorBlock):
    cfunc: chainer.functions.Tanh

    def __init__(self, cfunc: chainer.functions.Tanh):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        assert len(inputs) == 1
        opr = Tanh(generate_unique_name(self.cfunc.label))
        return opr(inputs[0])


class LinearBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.connection.linear.LinearFunction

    def __init__(self, cfunc: chainer.functions.connection.linear.LinearFunction):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        # noinspection PyUnresolvedReferences
        linear_opr = Linear(generate_unique_name(self.cfunc.label))
        x = inputs[0]
        w = inputs[1]
        if x.ndim == 4 and w.ndim == 2:
            # wを4次元に拡張 (NC -> NCHW)
            x_shape_dict = x.shape_dict
            w_shape_dict = w.shape_dict
            assert x_shape_dict[Axis.C] * x_shape_dict[Axis.H] * x_shape_dict[Axis.W] == w_shape_dict[Axis.C]
            assert w.order is OrderNC
            w.order = OrderNCHW
            w_new_shape = [w_shape_dict[Axis.N], x_shape_dict[Axis.C], x_shape_dict[Axis.H],
                           x_shape_dict[Axis.W]]
            w.shape = w_new_shape
            w.data = w.data.reshape(w_new_shape)

        opr_out, = linear_opr(inputs[0], inputs[1])
        if len(inputs) == 3:
            # biasあり
            # noinspection PyUnresolvedReferences
            bias_opr = AxiswiseBias(generate_unique_name(self.cfunc.label), axis=Axis.C)
            self.hidden_vars.append(opr_out)
            opr_out, = bias_opr(opr_out, inputs[2])
        return opr_out,


class Convolution2DBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.connection.convolution_2d.Convolution2DFunction

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.connection.convolution_2d.Convolution2DFunction):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        w = inputs[1]
        w_shape_dict = w.shape_dict
        conv_opr = Convolution2D(generate_unique_name(self.cfunc.label),
                                 ksize=(w_shape_dict[Axis.H], w_shape_dict[Axis.W]),
                                 stride=(self.cfunc.sy, self.cfunc.sx),
                                 padding=(self.cfunc.ph, self.cfunc.pw))

        opr_out, = conv_opr(inputs[0], inputs[1])
        opr_out.change_order(OrderNCHW)

        if len(inputs) == 3:
            # biasあり
            bias_opr = AxiswiseBias(generate_unique_name(self.cfunc.label), axis=Axis.C)
            self.hidden_vars.append(opr_out)
            opr_out, = bias_opr(opr_out, inputs[2])
        return opr_out,


class Deconvolution2DBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.connection.deconvolution_2d.Deconvolution2DFunction

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.connection.deconvolution_2d.Deconvolution2DFunction):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        w = inputs[1]
        w_shape_dict = w.shape_dict
        conv_opr = Deconvolution2D(generate_unique_name(self.cfunc.label),
                                   ksize=(w_shape_dict[Axis.H], w_shape_dict[Axis.W]),
                                   stride=(self.cfunc.sy, self.cfunc.sx),
                                   padding=(self.cfunc.ph, self.cfunc.pw))

        opr_out, = conv_opr(inputs[0], inputs[1])
        opr_out.change_order(OrderNCHW)

        if len(inputs) == 3:
            # biasあり
            bias_opr = AxiswiseBias(generate_unique_name(self.cfunc.label), axis=Axis.C)
            self.hidden_vars.append(opr_out)
            opr_out, = bias_opr(opr_out, inputs[2])
        return opr_out,


class MaxPooling2DBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.pooling.max_pooling_2d.MaxPooling2D

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.pooling.max_pooling_2d.MaxPooling2D):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        conv_opr = MaxPooling2D(generate_unique_name(self.cfunc.label),
                                ksize=(self.cfunc.kh, self.cfunc.kw),
                                stride=(self.cfunc.sy, self.cfunc.sx),
                                padding=(self.cfunc.ph, self.cfunc.pw))

        opr_out, = conv_opr(inputs[0])
        opr_out.change_order(OrderNCHW)

        return opr_out,


class AveragePooling2DBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.pooling.average_pooling_2d.AveragePooling2D

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.pooling.average_pooling_2d.AveragePooling2D):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        conv_opr = AveragePooling2D(generate_unique_name(self.cfunc.label),
                                    ksize=(self.cfunc.kh, self.cfunc.kw),
                                    stride=(self.cfunc.sy, self.cfunc.sx),
                                    padding=(self.cfunc.ph, self.cfunc.pw))

        opr_out, = conv_opr(inputs[0])
        opr_out.change_order(OrderNCHW)

        return opr_out,


class LocalResponseNormalizationBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.normalization.local_response_normalization.LocalResponseNormalization

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.normalization.local_response_normalization.LocalResponseNormalization):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        conv_opr = LocalResponseNormalization(generate_unique_name(self.cfunc.label),
                                              n=self.cfunc.n,
                                              k=self.cfunc.k,
                                              alpha=self.cfunc.alpha,
                                              beta=self.cfunc.beta)

        opr_out, = conv_opr(inputs[0])
        return opr_out,


class BatchNormalizationBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.normalization.batch_normalization.BatchNormalizationFunction

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.normalization.batch_normalization.BatchNormalizationFunction):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        if len(inputs) == 5:
            x, gamma, beta, mean, variance = inputs
            variance_data = variance.data
            mean_data = mean.data
        elif len(inputs) == 3:
            x, gamma, beta = inputs
            variance_data = self.cfunc.running_var
            mean_data = self.cfunc.running_mean
        else:
            raise ValueError("inputs to BatchNormalizationFunction have to be 5 or 3.")
        # x以外の変数は、加工して新しいConstantとして使う
        # (x - mean) / sqrt(var + eps) * gamma + beta
        # gamma_div_std = gamma / sqrt(var + eps)
        # beta_scaled = beta - mean * gamma_div_std
        # y = x * gamma_div_std + beta_scaled
        gamma_div_std = gamma.data / np.sqrt(variance_data + self.cfunc.eps)
        beta_scaled = beta.data - mean_data * gamma_div_std

        scale_opr = AxiswiseScale(generate_unique_name(self.cfunc.label), axis=Axis.C)
        gamma_div_std_const = ConstantVariable(gamma_div_std, OrderC)
        scale_out, = scale_opr(x, gamma_div_std_const)
        self.hidden_vars.append(scale_out)
        self.hidden_consts.append(gamma_div_std_const)

        offset_opr = AxiswiseBias(generate_unique_name(self.cfunc.label), axis=Axis.C)
        beta_scaled_const = ConstantVariable(beta_scaled, OrderC)
        offset_out, = offset_opr(scale_out, beta_scaled_const)
        self.hidden_consts.append(beta_scaled_const)

        return offset_out,


class AddBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.math.basic_math.Add

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.math.basic_math.Add):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        opr = ElementwiseSum(generate_unique_name(self.cfunc.label))
        return list(opr(*inputs))


class AddConstantBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.math.basic_math.AddConstant

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.math.basic_math.AddConstant):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        opr = ScalarAffine(generate_unique_name(self.cfunc.label), scale=1, bias=float(self.cfunc.value))
        return opr(*inputs)


class MulConstantBlock(OperatorBlock):
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.math.basic_math.MulConstant

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.math.basic_math.MulConstant):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> Tuple[Variable]:
        opr = ScalarAffine(generate_unique_name(self.cfunc.label), scale=float(self.cfunc.value), bias=0)
        return opr(*inputs)


class ReshapeBlock(OperatorBlock):
    # Currently, only removing HW axis is allowed
    # NCHW (n,c,h,w) => NC (n,c*h*w) (assuming c-order)
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.array.reshape.Reshape

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.array.reshape.Reshape):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        assert len(inputs) == 1
        # NCHWをNCにする場合のみ想定
        assert inputs[0].order is OrderNCHW
        assert len(self.cfunc.shape) == 2
        assert self.cfunc.shape[0] == inputs[0].shape[0]  # Nは変化しない

        opr = Flatten(generate_unique_name(self.cfunc.label), in_axes=[Axis.C, Axis.H, Axis.W], out_axis=Axis.C)
        return list(opr(inputs[0]))


class DropoutBlock(OperatorBlock):
    """
    Doing nothing (test-purpose)
    """
    # noinspection PyUnresolvedReferences
    cfunc: chainer.functions.noise.dropout.Dropout

    # noinspection PyUnresolvedReferences
    def __init__(self, cfunc: chainer.functions.noise.dropout.Dropout):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        return inputs


# noinspection PyUnresolvedReferences
BLOCK_CLASSES = [(chainer.functions.ReLU, ReluBlock),
                 (chainer.functions.ELU, EluBlock),
                 (chainer.functions.Tanh, TanhBlock),
                 (chainer.functions.connection.linear.LinearFunction, LinearBlock),
                 (chainer.functions.connection.convolution_2d.Convolution2DFunction, Convolution2DBlock),
                 (chainer.functions.connection.deconvolution_2d.Deconvolution2DFunction, Deconvolution2DBlock),
                 (chainer.functions.pooling.max_pooling_2d.MaxPooling2D, MaxPooling2DBlock),
                 (chainer.functions.pooling.average_pooling_2d.AveragePooling2D, AveragePooling2DBlock),
                 (chainer.functions.normalization.batch_normalization.BatchNormalizationFunction,
                  BatchNormalizationBlock),
                 (chainer.functions.math.basic_math.Add, AddBlock),
                 (chainer.functions.math.basic_math.AddConstant, AddConstantBlock),
                 (chainer.functions.math.basic_math.MulConstant, MulConstantBlock),
                 (chainer.functions.array.reshape.Reshape, ReshapeBlock),
                 (chainer.functions.normalization.local_response_normalization.LocalResponseNormalization,
                  LocalResponseNormalizationBlock),
                 (chainer.functions.noise.dropout.Dropout, DropoutBlock)]


class ChainerGraphConverter:
    def __init__(self):
        self._cvar_to_nvar = {}  # id(VariableNode) => Variable (note: chainerに対応しないVariableも作られる)
        self._cvar_ids = []  # id(VariableNode)
        self._known_nvars = []  # 存在するVariable(include Constant)

    def convert_from_inout_vars(self, inputs: List[chainer.Variable], outputs: List[chainer.Variable]):
        chainer_graph = chainer.computational_graph.build_computational_graph(outputs)
        return self.convert(chainer_graph, inputs, outputs)

    def convert(self, chainer_computational_graph: chainer.computational_graph.ComputationalGraph,
                input_vars: List[chainer.Variable], output_vars: List[chainer.Variable]) -> Graph:
        # 戦略
        # 生成済み変数(chainer.Variable)をセットに入れる; 入力変数およびウェイト
        # 生成済み変数だけを入力とし、未処理のchainer.Functionを変換し、生成済み変数セットに追加
        # 未処理のchainer.Functionがなくなったら終わり
        self._cvar_to_nvar = {}
        self._cvar_ids = []
        self._known_nvars = []
        self._convert_weight_vars(chainer_computational_graph)
        # Variable | VariableNodeをVariableNodeに変換
        if chainer_v2:
            input_vars = [v.node if isinstance(v, chainer.Variable) else v for v in input_vars]
            output_vars = [v.node if isinstance(v, chainer.Variable) else v for v in output_vars]
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
            nvar.attributes.add(Output)

        # このフレームワークで標準的なデータオーダーに変更
        self._transpose_vars(self._known_nvars)

        return Graph([self._cvar_to_nvar[id(cvar)] for cvar in input_vars],
                     [self._cvar_to_nvar[id(cvar)] for cvar in output_vars])

    def _convert_input_vars(self, input_vars: List[VariableNode]):
        for cvar in input_vars:
            nvar = self._convert_var(cvar)
            nvar.attributes.add(Input(nvar))

    def _convert_weight_vars(self, chainer_computational_graph: chainer.computational_graph.ComputationalGraph):
        # 名前付きの変数を変換

        # Phase1. 特殊ケースのみ先に処理
        for cvar in chainer_computational_graph.nodes:
            # noinspection PyUnresolvedReferences
            if isinstance(cvar, chainer.functions.normalization.batch_normalization.BatchNormalizationFunction):
                # BNのmean, varは名無しだがウェイト
                if len(cvar.inputs) == 5:  # data, gamma, bias, mean, var
                    self._convert_var(cvar.inputs[3], force_constant=True)
                    self._convert_var(cvar.inputs[4], force_constant=True)

            elif isinstance(cvar, chainer.functions.connection.deconvolution_2d.Deconvolution2DFunction):
                # chainerのDeconvolution2DのWは(Cin, Cout, Kh, Kw)のオーダー
                self._convert_var(cvar.inputs[1], force_constant=True, force_order=OrderCNHW)

        # Phase2. 残りを処理
        for cvar in chainer_computational_graph.nodes:
            # noinspection PyUnresolvedReferences
            if isinstance(cvar, VariableNode):
                if id(cvar) not in self._cvar_ids and cvar.name is not None:
                    self._convert_var(cvar)

    def _convert_var(self,
                     cvar: VariableNode,
                     force_constant=False,
                     force_order: Order = None):
        assert id(cvar) not in self._cvar_ids
        ndim = len(cvar.shape)
        if force_order:
            order = force_order

        else:
            if ndim == 4:
                # both weight and variable
                order = OrderNCHW
            elif ndim == 2:
                # both weight and variable
                order = OrderNC
            elif ndim == 1:
                # both weight and variable
                order = OrderC
            else:
                raise NotImplementedError()

        assert order.ndim == ndim

        if cvar.name is not None or force_constant:
            nvar = ConstantVariable(chainer.cuda.to_cpu(cvar.data), order)  # force on CPU
        else:
            nvar = Variable(cvar.shape, order)

        self._cvar_to_nvar[id(cvar)] = nvar
        self._cvar_ids.append(id(cvar))
        self._known_nvars.append(nvar)
        return nvar

    # noinspection PyMethodMayBeStatic
    def _construct_operator_block(self, cfunc: chainer.Function) -> OperatorBlock:
        for function_class, block_class in BLOCK_CLASSES:
            if isinstance(cfunc, function_class):
                return block_class(cfunc)
        raise ValueError("Unknown layer {}".format(type(cfunc)))

    # noinspection PyMethodMayBeStatic
    def _transpose_vars(self, nvars: List[Variable]):
        """
        変数を、標準的なAxisOrderに変更
        :param nvars: 
        :return: 
        """
        for nvar in nvars:
            if isinstance(nvar, ConstantVariable):
                if nvar.ndim == 1:
                    nvar.change_order(OrderC)
                elif nvar.ndim == 2:
                    nvar.change_order(OrderCN)
                elif nvar.ndim == 4:
                    assert len(nvar.input_to) == 1
                    first_input_to = list(nvar.input_to)[0]
                    if isinstance(first_input_to, Convolution2D):
                        nvar.change_order(OrderHWNC)
                    elif isinstance(first_input_to, Deconvolution2D):
                        nvar.change_order(OrderHWNC)
                    elif isinstance(first_input_to, Linear):
                        nvar.change_order(OrderHWCN)
                    else:
                        # 今の所ないはず
                        raise ValueError()
            else:
                if nvar.ndim == 1:
                    nvar.change_order(OrderC)
                elif nvar.ndim == 2:
                    nvar.change_order(OrderNC)
                elif nvar.ndim == 4:
                    nvar.change_order(OrderNHWC)
