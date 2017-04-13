# -*- coding:utf-8 -*-

"""
DNN Node
"""

from enum import Enum, auto
from typing import List, Set, Dict, Tuple
import numpy as np


class DNNLayerType(Enum):
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


class DNNLayerAttributes(Enum):
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


class DNNVariableAttributes(Enum):
    """
    変数の属性
    メモリ割り付けの際に利用
    """

    Input = auto()  # DNNへの入力
    Output = auto()  # DNNへの出力


class DNNVariable:
    """
    レイヤー間で受け渡される変数
    名前で識別される
    現在のところ、float32型(4byte/element)を想定している
    shapeは、(n, c)または(n, h, w, c) n: バッチサイズ、 c: チャンネルサイズ
    必ず、最初がバッチサイズ、最後がchannel
    """
    instances = {}

    def __init__(self, name: str, shape: Tuple, attributes: Set[DNNVariableAttributes] = None):
        assert name not in DNNVariable.instances
        if attributes is None:
            attributes = set()
        self.name = name
        self.shape = shape
        self.attributes = attributes
        DNNVariable.instances[name] = self

    @classmethod
    def get(cls, name):
        return cls.instances[name]


class DNNLayer:
    def __init__(self, name: str, layer_type: DNNLayerType, attributes: Set[DNNLayerAttributes],
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


class DNNLinearLayer(DNNLayer):
    """
    行列積レイヤー(bias含まず)
    Convolutionの後に接続する場合、Reshapeレイヤーで2次元入力(n, c)に変換してから入力する
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights['W']: (in_size, out_size)
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert 'W' in weights
        assert 'in_size' in parameters
        assert 'out_size' in parameters
        super().__init__(name, DNNLayerType.Linear, DNNLinearLayer.ATTRIBUTES, parameters, weights)


class DNNChannelwiseBiasLayer(DNNLayer):
    """
    Channelwiseにウェイトを加算するレイヤー
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.Channelwise,
                  DNNLayerAttributes.Inplace,
                  DNNLayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights['b']: (out_size, )
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert 'b' in weights
        assert 'out_size' in parameters
        super().__init__(name, DNNLayerType.ChannelwiseBias, DNNChannelwiseBiasLayer.ATTRIBUTES, parameters, weights)


class DNNChannelwiseScaleLayer(DNNLayer):
    """
    Channelwiseにウェイトを乗算するレイヤー
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.Channelwise,
                  DNNLayerAttributes.Inplace,
                  DNNLayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        super().__init__(name, DNNLayerType.ChannelwiseScale, DNNChannelwiseScaleLayer.ATTRIBUTES, parameters, weights)


class DNNReluLayer(DNNLayer):
    """
    Reluレイヤー
    """
    # ElementwiseであればChannelwiseだが、このattribute定義がよいのかどうか？
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.Elementwise,
                  DNNLayerAttributes.Channelwise,
                  DNNLayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        super().__init__(name, DNNLayerType.Relu, DNNReluLayer.ATTRIBUTES, parameters, weights)


class DNNSigmoidLayer(DNNLayer):
    """
    Sigmoidレイヤー
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.Elementwise,
                  DNNLayerAttributes.Channelwise,
                  DNNLayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        super().__init__(name, DNNLayerType.Sigmoid, DNNSigmoidLayer.ATTRIBUTES, parameters, weights)


class DNNConvolution2DLayer(DNNLayer):
    """
    Convolutionレイヤー(bias含まず)
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights['W']: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int],
         cover_all: Boolean=False}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert 'W' in weights
        assert 'in_size' in parameters
        assert 'out_size' in parameters
        super().__init__(name, DNNLayerType.Convolution2D, DNNConvolution2DLayer.ATTRIBUTES, parameters, weights)


class DNNDeconvolution2DLayer(DNNLayer):
    """
    Deconvolutionレイヤー(bias含まず)
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.HaveWeights}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        """
        weights['W']: (kh, kw, in_size, out_size)
        parameters: {in_size: int, out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert len(weights) == 1
        assert 'W' in weights
        assert 'in_size' in parameters
        assert 'out_size' in parameters
        super().__init__(name, DNNLayerType.Deconvolution2D, DNNDeconvolution2DLayer.ATTRIBUTES, parameters, weights)


class DNNMaxPooling2DLayer(DNNLayer):
    """
    Max pooling (2D) レイヤー
    padding挙動はchainer準拠 (cover_allに注意)
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int], cover_all: Boolean=True}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert 'out_size' in parameters
        super().__init__(name, DNNLayerType.MaxPooling2D, DNNMaxPooling2DLayer.ATTRIBUTES, parameters, weights)


class DNNAveragePooling2DLayer(DNNLayer):
    """
    Average pooling (2D) レイヤー
    padding挙動はchainer準拠
    当面はglobal average poolingだけ実装
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_size: int, ksize: Tuple[int, int], stride: Tuple[int, int], pad: Tuple[int, int]}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert 'out_size' in parameters
        super().__init__(name, DNNLayerType.AveragePooling2D, DNNAveragePooling2DLayer.ATTRIBUTES, parameters, weights)


class DNNConcatLayer(DNNLayer):
    """
    n入力を連結するレイヤー
    結合軸はparametersで指定(chainerと同じ挙動)
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {axis: int, n_inputs: int}
        n_inputs: 入力変数の数
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert 'axis' in parameters
        assert 'n_inputs' in parameters
        # 結合軸方向の各データの次元数がいる？
        super().__init__(name, DNNLayerType.Concat, DNNConcatLayer.ATTRIBUTES, parameters, weights,
                         n_inputs=parameters['n_inputs'])


class DNNElementwiseSumLayer(DNNLayer):
    """
    n入力を加算するレイヤー
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.FirstInplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {n_inputs: int}
        n_inputs: 入力変数の数
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert 'axis' in parameters
        assert 'n_inputs' in parameters
        super().__init__(name, DNNLayerType.ElementwiseSum, DNNElementwiseSumLayer.ATTRIBUTES, parameters, weights,
                         n_inputs=parameters['n_inputs'])


class DNNReshapeLayer(DNNLayer):
    """
    入力変数の形を変形するレイヤー
    形状変化を表現する便宜上のもので、データ操作はない
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise,
                  DNNLayerAttributes.PostChannelwise,
                  DNNLayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray] = None):
        """
        parameters: {out_shape: Tuple}
        :param name: 
        :param parameters: 
        :param weights: 
        """
        assert 'out_shape' in parameters
        super().__init__(name, DNNLayerType.Reshape, DNNReshapeLayer.ATTRIBUTES, parameters, weights)


class DNNGraphNode:
    def __init__(self, name: str, layer: DNNLayer, bottoms: List[DNNVariable], tops: List[DNNVariable]):
        self.name = name
        self.layer = layer
        self.bottoms = bottoms
        self.tops = tops


class DNNGraph:
    def __init__(self, nodes: List[DNNGraphNode], inputs: List[DNNVariable], outputs: List[DNNVariable],
                 batch_size: int):
        self.nodes = nodes
        self.inputs = inputs
        self.outputs = outputs
        self.batch_size = batch_size


class DNNGraphOptimizer:
    def __init__(self, graph):
        self.graph = graph

    def optimize(self):
        while True:
            variable_to_node = self._get_variable_to_node()
            for variable, prod_cons in variable_to_node.items():
                # ある変数からみて生成側と消費側がくっつくかどうか判定
                prod = prod_cons['producer']
                cons_list = prod_cons['consumers']
                cons_first = cons_list[0] if len(cons_list) > 0 else None
                if prod is not None \
                        and DNNLayerAttributes.PostElementwise in prod.layer.attributes \
                        and len(cons_list) == 1 \
                        and DNNLayerAttributes.Elementwise in cons_first.layer.attributes:
                    # linearのうしろにreluをくっつける
                    prod.layer.append_child_to_tail(cons_first.layer)
                    # linearの出力がreluの出力になる
                    prod.tops[0] = cons_first.tops[0]
                    # 後続レイヤーが持たないattributeを消す(これでいいのか？)
                    prod.layer.attributes &= cons_first.layer.attributes
                    # reluのノードは消える (同時に、linear-relu間の変数もなくなる)
                    self.graph.nodes.remove(cons_first)
                    break  # グラフが変わったのでvariable_to_nodeをつくりなおす
                if prod is not None \
                        and DNNLayerAttributes.PostChannelwise in prod.layer.attributes \
                        and len(cons_list) == 1 \
                        and DNNLayerAttributes.Channelwise in cons_first.layer.attributes:
                    # linearのうしろにbiasをくっつける
                    prod.layer.append_child_to_tail(cons_first.layer)
                    # linearの出力がbiasの出力になる
                    prod.tops[0] = cons_first.tops[0]
                    # 後続レイヤーが持たないattributeを消す(これでいいのか？)
                    prod.layer.attributes &= cons_first.layer.attributes
                    # biasのノードは消える (同時に、linear-bias間の変数もなくなる)
                    self.graph.nodes.remove(cons_first)
                    break  # グラフが変わったのでvariable_to_nodeをつくりなおす
            else:
                # グラフが変化しなかった
                break

    def _get_variable_to_node(self):
        """
        変数からみた、作成者および消費者ノード情報の作成
        """
        variable_to_node = {}
        for node in self.graph.nodes:
            for bottom in node.bottoms:
                if bottom.name not in variable_to_node:
                    variable_to_node[bottom.name] = {'producer': None, 'consumers': []}
                variable_to_node[bottom.name]['consumers'].append(node)

            for top in node.tops:
                if top.name not in variable_to_node:
                    variable_to_node[top.name] = {'producer': None, 'consumers': []}
                variable_to_node[top.name]['producer'] = node
        return variable_to_node
