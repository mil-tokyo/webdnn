# -*- coding:utf-8 -*-

"""
DNN Node
"""

from enum import Enum, auto
from typing import List, Set, Dict, Tuple
import numpy as np


class LayerType(Enum):
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


class LayerAttributes(Enum):
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


class Variable:
    """
    レイヤー間で受け渡される変数
    名前で識別される
    現在のところ、float32型(4byte/element)を想定している
    shapeは、(n, c)または(n, h, w, c) n: バッチサイズ、 c: チャンネルサイズ
    必ず、最初がバッチサイズ、最後がchannel
    """
    instances = {}

    def __init__(self, name: str, shape: Tuple, attributes: Set[VariableAttributes] = None):
        assert name not in Variable.instances
        if attributes is None:
            attributes = set()
        self.name = name
        self.shape = shape
        self.attributes = attributes
        Variable.instances[name] = self

    @classmethod
    def get(cls, name):
        return cls.instances[name]


class Layer:
    def __init__(self, name: str, layer_type: LayerType, attributes: Set[LayerAttributes],
                 parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None,
                 n_inputs: int = 1, n_outputs: int = 1, next_node=None):
        self.name = name
        self.layer_type = layer_type
        self.attributes = attributes
        self.parameters = parameters
        self.weights = weights if weights is not None else dict()
        # 今の所、1出力レイヤーの後ろに1入力1出力レイヤーをくっつけるだけの機能
        # 連結グラフとして表現
        self.next_node = next_node
        self.is_root = True  # 誰かの子でない
        self.n_inputs = n_inputs  # 入力変数の数
        self.n_outputs = n_outputs  # 出力変数の数

    def iterate_self_and_children(self):
        yield self
        if self.next_node is not None:
            for child in self.next_node.iterate_self_and_children():
                yield child

    def append_child_to_tail(self, layer):
        """
        連結グラフの末尾にレイヤーをくっつける
        """
        layer.is_root = False
        if self.next_node is None:
            assert self.n_outputs == self.n_inputs
            self.next_node = layer
        else:
            self.next_node.append_child_to_tail(layer)


class LinearLayer(Layer):
    """
    行列積レイヤー(bias含まず)
    Convolutionの後に接続する場合、Reshapeレイヤーで2次元入力(n, c)に変換してから入力する
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights["W"]: (in_size, out_size)
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert "W" in weights
        assert "in_size" in parameters
        assert "out_size" in parameters
        super().__init__(name, LayerType.Linear, LinearLayer.ATTRIBUTES, parameters, weights)


class ChannelwiseBiasLayer(Layer):
    """
    Channelwiseにウェイトを加算するレイヤー
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.Channelwise,
                  LayerAttributes.Inplace,
                  LayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights["b"]: (out_size, )
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert "b" in weights
        assert "out_size" in parameters
        super().__init__(name, LayerType.ChannelwiseBias, ChannelwiseBiasLayer.ATTRIBUTES, parameters, weights)


class ChannelwiseScaleLayer(Layer):
    """
    Channelwiseにウェイトを乗算するレイヤー
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.Channelwise,
                  LayerAttributes.Inplace,
                  LayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        super().__init__(name, LayerType.ChannelwiseScale, ChannelwiseScaleLayer.ATTRIBUTES, parameters, weights)


class ReluLayer(Layer):
    """
    Reluレイヤー
    """
    # ElementwiseであればChannelwiseだが、このattribute定義がよいのかどうか？
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.Elementwise,
                  LayerAttributes.Channelwise,
                  LayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        super().__init__(name, LayerType.Relu, ReluLayer.ATTRIBUTES, parameters, weights)


class SigmoidLayer(Layer):
    """
    Sigmoidレイヤー
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.Elementwise,
                  LayerAttributes.Channelwise,
                  LayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        super().__init__(name, LayerType.Sigmoid, SigmoidLayer.ATTRIBUTES, parameters, weights)


class Convolution2DLayer(Layer):
    """
    Convolutionレイヤー(bias含まず)
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int],
         cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert "W" in weights
        assert "in_size" in parameters
        assert "out_size" in parameters
        super().__init__(name, LayerType.Convolution2D, Convolution2DLayer.ATTRIBUTES, parameters, weights)


class Deconvolution2DLayer(Layer):
    """
    Deconvolutionレイヤー(bias含まず)
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights["W"]: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert "W" in weights
        assert "in_size" in parameters
        assert "out_size" in parameters
        super().__init__(name, LayerType.Deconvolution2D, Deconvolution2DLayer.ATTRIBUTES, parameters, weights)


class MaxPooling2DLayer(Layer):
    """
    Max pooling (2D) レイヤー
    padding挙動はchainer準拠 (cover_allに注意)
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=True}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "out_size" in parameters
        super().__init__(name, LayerType.MaxPooling2D, MaxPooling2DLayer.ATTRIBUTES, parameters, weights)


class AveragePooling2DLayer(Layer):
    """
    Average pooling (2D) レイヤー
    padding挙動はchainer準拠
    当面はglobal average poolingだけ実装
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "out_size" in parameters
        super().__init__(name, LayerType.AveragePooling2D, AveragePooling2DLayer.ATTRIBUTES, parameters, weights)


class ConcatLayer(Layer):
    """
    n入力を連結するレイヤー
    結合軸はparametersで指定(chainerと同じ挙動)
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {axis: int, n_inputs: int}
        n_inputs: 入力変数の数
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "axis" in parameters
        assert "n_inputs" in parameters
        # 結合軸方向の各データの次元数がいる？
        super().__init__(name, LayerType.Concat, ConcatLayer.ATTRIBUTES, parameters, weights,
                         n_inputs=parameters["n_inputs"])


class ElementwiseSumLayer(Layer):
    """
    n入力を加算するレイヤー
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.FirstInplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {n_inputs: int}
        n_inputs: 入力変数の数
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "axis" in parameters
        assert "n_inputs" in parameters
        super().__init__(name, LayerType.ElementwiseSum, ElementwiseSumLayer.ATTRIBUTES, parameters, weights,
                         n_inputs=parameters["n_inputs"])


class ReshapeLayer(Layer):
    """
    入力変数の形を変形するレイヤー
    形状変化を表現する便宜上のもので、データ操作はない
    """
    ATTRIBUTES = {LayerAttributes.PostElementwise,
                  LayerAttributes.PostChannelwise,
                  LayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_shape: Tuple}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert "out_shape" in parameters
        super().__init__(name, LayerType.Reshape, ReshapeLayer.ATTRIBUTES, parameters, weights)


class GraphNode:
    def __init__(self, name: str, layer: Layer, bottoms: List[Variable], tops: List[Variable]):
        self.name = name
        self.layer = layer
        self.bottoms = bottoms
        self.tops = tops


class Graph:
    def __init__(self, nodes: List[GraphNode], inputs: List[Variable], outputs: List[Variable],
                 batch_size: int):
        self.nodes = nodes
        self.inputs = inputs
        self.outputs = outputs
        self.batch_size = batch_size
