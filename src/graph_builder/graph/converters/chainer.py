# -*- coding:utf-8 -*-

"""
Chainer Link -> Graph object converters
Assuming Chainer 1.23
"""

from typing import Dict, Set, List, Iterable
import numpy as np
import chainer
import chainer.computational_graph
import chainer.functions as F
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

    def __init__(self):
        self.hidden_vars = []

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        raise NotImplementedError()


class ReluBlock(OperatorBlock):
    cfunc: chainer.functions.ReLU

    def __init__(self, cfunc: chainer.functions.ReLU):
        super().__init__()
        self.cfunc = cfunc

    def __call__(self, inputs: List[Variable]) -> List[Variable]:
        opr = operators.Relu(generate_unique_name(self.cfunc.label), {})
        return opr(*inputs)


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
            assert x_shape_dict["C"] * x_shape_dict["H"] * x_shape_dict["W"] == w_shape_dict["C"]
            assert w.axis_order is VA.OrderNC
            w.attributes.remove(VA.OrderNC)
            w.attributes.add(VA.OrderNCHW)
            w.axis_order = VA.OrderNCHW
            w_new_shape = [w_shape_dict["N"], x_shape_dict["C"], x_shape_dict["H"], x_shape_dict["W"]]
            w.shape = w_new_shape
            w.data = w.data.reshape(w_new_shape)

        opr_out, = linear_opr(inputs[0], inputs[1])
        if len(inputs) == 3:
            # biasあり
            bias_opr = operators.AxiswiseBias(generate_unique_name(self.cfunc.label), {"axis": A.Axis.C})
            self.hidden_vars.append(opr_out)
            opr_out, = bias_opr(opr_out, inputs[2])
        return opr_out,


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
                                           {"ksize": (w_shape_dict["H"], w_shape_dict["W"]),
                                            "stride": (self.cfunc.sy, self.cfunc.sx),
                                            "padding": (self.cfunc.ph, self.cfunc.pw)})

        opr_out, = conv_opr(inputs[0], inputs[1])
        if len(inputs) == 3:
            # biasあり
            bias_opr = operators.AxiswiseBias(generate_unique_name(self.cfunc.label), {"axis": A.Axis.C})
            self.hidden_vars.append(opr_out)
            opr_out, = bias_opr(opr_out, inputs[2])
        return opr_out,


BLOCK_CLASSES = [(chainer.functions.ReLU, ReluBlock),
                 (chainer.functions.connection.linear.LinearFunction, LinearBlock),
                 (chainer.functions.connection.convolution_2d.Convolution2DFunction, Convolution2DBlock)]


class ChainerGraphConverter:
    def __init__(self):
        self._cvar_to_nvar = {}
        self._cvar_ids = []

    def convert(self, chainer_computational_graph: chainer.computational_graph.ComputationalGraph,
                input_vars: List[chainer.Variable], output_vars: List[chainer.Variable]) -> Node:
        # 戦略
        # 生成済み変数(chainer.Variable)をセットに入れる; 入力変数およびウェイト
        # 生成済み変数だけを入力とし、未処理のchainer.Functionを変換し、生成済み変数セットに追加
        # 未処理のchainer.Functionがなくなったら終わり
        self._cvar_to_nvar = {}
        self._cvar_ids = []
        self._convert_weight_vars(chainer_computational_graph)
        self._convert_input_vars(input_vars)

        print("nodes: {}".format(chainer_computational_graph.nodes))
        pending_functions = [cfunc for cfunc in chainer_computational_graph.nodes if
                             isinstance(cfunc, chainer.Function)]
        print("pendings: {}".format(pending_functions))
        while len(pending_functions) > 0:
            for cfunc in pending_functions:
                if all(((id(cvar) in self._cvar_ids) for cvar in cfunc.inputs)):
                    # このレイヤーは入力が揃った
                    print(cfunc)
                    opr_block = self._construct_operator_block(cfunc)
                    out_nvars = opr_block([self._cvar_to_nvar[id(cvar)] for cvar in cfunc.inputs])
                    # 出力変数を対応づける
                    for out_nvar, out_cvar_wref in zip(out_nvars, cfunc.outputs):
                        out_cvar = out_cvar_wref()
                        print(out_nvar.shape, out_cvar.shape)
                        assert tuple(out_nvar.shape) == out_cvar.shape
                        self._cvar_to_nvar[id(out_cvar)] = out_nvar
                        self._cvar_ids.append(id(out_cvar))
                    pending_functions.remove(cfunc)
                    break  # for cfunc in pending_functions
            else:
                raise ValueError("inputs to functions cannot be resolved.")

        # 出力変数にAttributeをつける
        for cvar in output_vars:
            if id(cvar) not in self._cvar_ids:
                raise ValueError("Output variable is not generated by graph.")
            nvar = self._cvar_to_nvar[id(cvar)]
            nvar.attributes.add(VA.Output)

        # 便宜的に、最初の入力変数に対応するNodeを返す (あとでかえるかも)
        return self._cvar_to_nvar[id(input_vars[0])]

    def _convert_input_vars(self, input_vars: Iterable[chainer.Variable]):
        for cvar in input_vars:
            print("input {}".format(cvar))
            self._convert_var(cvar, attrs={VA.Input})

    def _convert_weight_vars(self, chainer_computational_graph: chainer.computational_graph.ComputationalGraph):
        # 名前付きの変数を変換
        for cvar in chainer_computational_graph.nodes:
            if isinstance(cvar, chainer.Variable):
                if cvar.name is not None:
                    print(cvar.name)
                    self._convert_var(cvar)
            elif isinstance(cvar, chainer.functions.BatchNormalization):
                # TODO: BNのmean, varは名無しだがウェイト
                raise NotImplementedError()

    def _convert_var(self, cvar: chainer.Variable, attrs: Iterable[Attribute] = None, force_constant=False):
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
        return nvar

    def _construct_operator_block(self, cfunc: chainer.Function) -> OperatorBlock:
        for function_class, block_class in BLOCK_CLASSES:
            if isinstance(cfunc, function_class):
                return block_class(cfunc)
        raise ValueError("Unknown layer {}".format(type(cfunc)))
