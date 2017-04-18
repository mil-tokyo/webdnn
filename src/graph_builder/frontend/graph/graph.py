# -*- coding:utf-8 -*-

"""
DNN Node
"""

from enum import Enum, auto
from typing import List, Set, Dict, Tuple, Iterable, NamedTuple

import numpy as np


class OperatorType(Enum):
    Unknown = auto()
    Linear = auto()
    Convolution2D = auto()
    ChannelwiseBias = auto()
    ChannelwiseScale = auto()
    Relu = auto()
    Sigmoid = auto()
    Deconvolution2D = auto()
    MaxPooling2D = auto()
    AveragePooling2D = auto()
    Concat = auto()
    ElementwiseSum = auto()
    Reshape = auto()


class OperatorAttribute(Enum):
    """
    レイヤーの属性
    複数のレイヤーが連結される際は、連結されたレイヤー全体を表す属性をルートのレイヤーに付与
    """

    Inplace = auto()  # 入出力メモリが同じアドレスでよい（違っていても良い）
    FirstInplace = auto()  # 最初の入力および出力メモリが同じアドレスで良い(A=A+B)（違っていても良い）
    HaveWeights = auto()  # ウェイトを持つ
    Elementwise = auto()  # 全要素に同じ処理をするレイヤー
    Channelwise = auto()  # 最内ループのインデックスごとに違う処理をするレイヤー
    PostElementwise = auto()  # 後ろにElementwiseを接続できる
    PostChannelwise = auto()  # 後ろにChannelwiseを接続できる


class VariableAttributes(Enum):
    """
    変数の属性
    メモリ割り付けの際に利用
    """

    Input = auto()  # DNNへの入力
    Output = auto()  # DNNへの出力
    Constant = auto()


class Variable:
    """
    レイヤー間で受け渡される変数
    名前で識別される
    現在のところ、float32型(4byte/element)を想定している
    shapeは、(n, c)または(n, h, w, c) n: バッチサイズ、 c: チャンネルサイズ
    必ず、最初がバッチサイズ、最後がchannel
    """

    instances: Dict[str, "Variable"] = {}
    shape: List[int]
    attributes: Set[VariableAttributes]
    input_to: Set["Operator"]
    output_from: "Operator" = None

    def __init__(self, shape: List[int], attributes: Set[VariableAttributes] = None):
        self.shape = list(shape)
        self.attributes = attributes
        self.input_to = set()

    @classmethod
    def get(cls, name):
        return cls.instances[name]

    @property
    def size(self):
        return np.prod(self.shape)

    def __repr__(self):
        return f"<Variable shape={self.shape}>"

    def __str__(self):
        return self.__repr__()


class ConstantVariable(Variable):
    data: np.array

    def __init__(self, data: np.array, attributes: Set[VariableAttributes] = None):
        attributes = attributes if attributes is not None else set()
        attributes.add(VariableAttributes.Constant)
        self.data = data

        super(ConstantVariable, self).__init__(data.shape, attributes)


class Operator:
    name: str
    attributes: Set[OperatorAttribute] = []
    weights: Dict[str, np.ndarray]
    inputs: Set[Variable]
    outputs: Set[Variable]

    def __init__(self,
                 name: str,
                 parameters: Dict[str, object] = None,
                 weights: Dict[str, np.ndarray] = None,
                 inputs: Set[Variable] = None,
                 outputs: Set[Variable] = None):
        parameters = parameters if parameters is not None else {}
        weights = weights if weights is not None else {}
        inputs = inputs if inputs is not None else set()
        outputs = outputs if outputs is not None else set()

        self.name = name
        self.attributes = set(self.attributes)  # copy construction
        self.parameters = parameters
        self.weights = weights
        self.inputs = inputs
        self.outputs = outputs

        for var in inputs:
            self.append_input(var)

        for var in outputs:
            self.remove_input(var)

    def append_input(self, var: Variable):
        self.inputs.add(var)
        var.input_to.add(self)

    def remove_input(self, var: Variable):
        if var not in self.inputs:
            raise KeyError(f"{var} is not input of {self}")

        self.inputs.remove(var)
        var.input_to.remove(self)

    def append_output(self, var: Variable):
        if var.output_from is not None:
            raise KeyError(f"{var} has been registered as output already.")

        self.outputs.add(var)
        var.output_from = self

    def remove_output(self, var: Variable):
        if var not in self.outputs:
            raise KeyError(f"{var} is not output of {self}")

        self.outputs.remove(var)
        var.output_from = None

    def __repr__(self):
        return f"""<Operator inputs={self.inputs}, outputs={self.outputs}>"""

    def __str__(self):
        return self.__repr__()


class LinearOperator(Operator):
    """
    行列積レイヤー(bias含まず)
    Convolutionの後に接続する場合、Reshapeレイヤーで2次元入力(n, c)に変換してから入力する
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        weights["W"]: (in_size, out_size)
        :param name: 
        :param parameters: 
        """
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        self.append_input(x)
        y = Variable([x.shape[0], w.shape[1]])
        self.append_output(y)
        return y


class ChannelwiseBiasOperator(Operator):
    """
    Channelwiseにウェイトを加算するレイヤー
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.Channelwise,
                  OperatorAttribute.Inplace,
                  OperatorAttribute.HaveWeights}

    def __init__(self, name: str):
        super().__init__(name)

    def __call__(self, x: Variable, b: Variable):
        y = Variable(x.shape)
        self.append_input(x)
        self.append_input(b)
        self.append_output(y)
        return y


class ChannelwiseScaleOperator(Operator):
    """
    Channelwiseにウェイトを乗算するレイヤー
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.Channelwise,
                  OperatorAttribute.Inplace,
                  OperatorAttribute.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        super().__init__(name, parameters)

    def __call__(self, x: Variable, s: Variable):
        y = Variable(x.shape)
        self.append_input(x)
        self.append_input(s)
        self.append_output(y)
        return y


class ReluOperator(Operator):
    """
    Reluレイヤー
    """
    # ElementwiseであればChannelwiseだが、このattribute定義がよいのかどうか？
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.Elementwise,
                  OperatorAttribute.Channelwise,
                  OperatorAttribute.Inplace}

    def __init__(self, name: str):
        super().__init__(name)

    def __call__(self, x: Variable):
        y = Variable(x.shape)
        self.append_input(x)
        self.append_output(y)
        return y


class SigmoidOperator(Operator):
    """
    Sigmoidレイヤー
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.Elementwise,
                  OperatorAttribute.Channelwise,
                  OperatorAttribute.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object]):
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        y = Variable(x.shape)
        self.append_input(x)
        self.append_output(y)
        return y


class Convolution2DOperator(Operator):
    """
    Convolutionレイヤー(bias含まず)
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "ksize" in parameters
        assert "stride" in parameters
        assert "padding" in parameters
        assert "in_size" in parameters
        assert "out_size" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        N = x.shape[0]
        H2 = (x.shape[1] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) / self.parameters["stride"][0] + 1
        W2 = (x.shape[2] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) / self.parameters["stride"][1] + 1
        C2 = self.parameters["out_size"]

        y = Variable([N, H2, W2, C2])
        self.append_input(x)
        self.append_input(w)
        self.append_output(y)
        return y


class Deconvolution2DOperator(Operator):
    """
    Deconvolutionレイヤー(bias含まず)
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "ksize" in parameters
        assert "stride" in parameters
        assert "padding" in parameters
        assert "in_size" in parameters
        assert "out_size" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable, w: Variable):
        N = x.shape[0]
        H2 = (x.shape[1] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) / self.parameters["stride"][0] + 1
        W2 = (x.shape[2] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) / self.parameters["stride"][1] + 1
        C2 = self.parameters["out_size"]

        y = Variable([N, H2, W2, C2])
        self.append_input(x)
        self.append_input(w)
        self.append_output(y)
        return y


class MaxPooling2DOperator(Operator):
    """
    Max pooling (2D) レイヤー
    padding挙動はchainer準拠 (cover_allに注意)
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "ksize" in parameters
        assert "stride" in parameters
        assert "padding" in parameters
        assert "in_size" in parameters
        assert "out_size" in parameters
        super().__init__(name, parameters)

    def __call__(self, x: Variable):
        N = x.shape[0]
        H2 = (x.shape[1] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) / self.parameters["stride"][0] + 1
        W2 = (x.shape[2] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) / self.parameters["stride"][1] + 1
        C2 = self.parameters["out_size"]

        y = Variable([N, H2, W2, C2])
        self.append_input(x)
        self.append_output(y)
        return y


class AveragePooling2DOperator(Operator):
    """
    Average pooling (2D) レイヤー
    padding挙動はchainer準拠
    当面はglobal average poolingだけ実装
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "out_size" in parameters
        super().__init__(name, parameters, weights)

    def __call__(self, x: Variable):
        N = x.shape[0]
        H2 = (x.shape[1] + 2 * self.parameters["padding"][0] - self.parameters["ksize"][0]) / self.parameters["stride"][0] + 1
        W2 = (x.shape[2] + 2 * self.parameters["padding"][1] - self.parameters["ksize"][1]) / self.parameters["stride"][1] + 1
        C2 = self.parameters["out_size"]

        y = Variable([N, H2, W2, C2])
        self.append_input(x)
        self.append_output(y)
        return y


class ConcatOperator(Operator):
    """
    n入力を連結するレイヤー
    結合軸はparametersで指定(chainerと同じ挙動)
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {axis: int, n_inputs: int}
        n_inputs: 入力変数の数
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "axis" in parameters
        super().__init__(name, parameters)

    def __call__(self, *xs: Variable):
        axis = self.parameters["axis"]  # type: int
        y_shape = list(xs[0].shape)  # type: List[int]
        y_shape[axis] = 0
        for x in xs:
            self.append_input(x)
            y_shape[axis] += x.shape[axis]

        y = Variable(y_shape)
        self.append_output(y)
        return y


class ElementwiseSumOperator(Operator):
    """
    n入力を加算するレイヤー
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.FirstInplace}

    def __init__(self, name: str, parameters: Dict[str, object]):
        """
        parameters: {n_inputs: int}
        n_inputs: 入力変数の数
        :param name: 
        :param parameters: 
        """
        super().__init__(name, parameters)

    def __call__(self, *xs: Variable):
        y = Variable(xs[0].shape)
        for x in xs:
            self.append_input(x)
        self.append_output(y)
        return y


class ReshapeOperator(Operator):
    """
    入力変数の形を変形するレイヤー
    形状変化を表現する便宜上のもので、データ操作はない
    """
    attributes = {OperatorAttribute.PostElementwise,
                  OperatorAttribute.PostChannelwise,
                  OperatorAttribute.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_shape: Tuple}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "out_shape" in parameters
        super().__init__(name, parameters, weights)

    def __call__(self, x: Variable):
        out_shape = self.parameters["out_shape"]  # type: List[int]
        y = Variable(out_shape)
        self.append_input(x)
        self.append_output(y)
        return y


class CompositeOperator(Operator):
    @classmethod
    def composite_with_ops(cls, name: str, ops: Iterable[Operator]):
        composite = CompositeOperator(name)

        inputs_or_hiddens: Set[Variable] = set()
        outputs_or_hiddens: Set[Variable] = set()

        for op in ops:
            inputs_or_hiddens.update(op.inputs)
            outputs_or_hiddens.update(op.outputs)

        inputs: Set[Variable] = inputs_or_hiddens.difference(outputs_or_hiddens)
        outputs: Set[Variable] = outputs_or_hiddens.difference(inputs_or_hiddens)

        for var in inputs:

            # FIXME
            var_alias = None

            for op in var.input_to:  # type: Operator
                if op in ops:
                    op.remove_input(var)
                    # op.append_input(var_alias)
                    composite.append_input(var)

        for var in outputs:
            # FIXME
            var_alias = None

            var.output_from.remove_output(var)
            # var.output_from.append_output(var_alias)
            composite.append_output(var)

        return composite

    @classmethod
    def composite_with_vars(cls, name: str, inputs: Iterable[Variable], outputs: Iterable[Variable]) -> "CompositeOperator":
        # グラフを辿って必要なopsを全て取ってくる
        inputs = set(inputs)
        var_queue: List[Variable] = list(outputs)
        ops: Set[Operator] = set()

        while len(var_queue) > 0:
            var = var_queue.pop(0)
            op = var.output_from
            if op is None or op in ops:
                continue

            ops.add(op)
            for var in op.inputs:
                if var in inputs:
                    continue

                var_queue.append(var)

        return CompositeOperator.composite_with_ops(name, ops)
