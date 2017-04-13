# -*- coding:utf-8 -*-

"""
DNN Node
"""

from enum import Enum, auto
from typing import List, Set, Dict, Tuple
import numpy as np

class DNNLayerType(Enum):
    Custom = auto()
    Linear = auto()
    Bias = auto()
    Scale = auto()
    Relu = auto()

class DNNLayerAttributes(Enum):
    Inplace = auto()#入出力メモリが同じアドレスでよい（違っていても良い）
    Elementwise = auto()
    Channelwise = auto()#最内ループのインデックスごとに違う処理をするレイヤー
    PostElementwise = auto()#後ろにElementwiseを接続できる
    PostChannelwise = auto()#後ろにChannelwiseを接続できる

class DNNVariableAttributes(Enum):
    Input = auto()
    Output = auto()

class DNNVariable:
    instances = {}
    def __init__(self, name: str, shape: Tuple[int], attributes: Set[DNNVariableAttributes]):
        assert name not in DNNVariable.instances
        self.name = name
        self.shape = shape
        DNNVariable.instances[name] = self
    
    @classmethod
    def get(cls, name):
        return cls.instances[name]

class DNNLayer:
    def __init__(self, name: str, layer_type: DNNLayerType, attributes: Set[DNNLayerAttributes], parameters: Dict[str, object], weights: Dict[str, np.ndarray]=None, next_node=None):
        self.name = name
        self.layer_type = layer_type
        self.attributes = attributes
        self.parameters = parameters
        self.weights = weights if weights is not None else dict()
        # 今の所、1出力レイヤーの後ろに1入力1出力レイヤーをくっつけるだけの機能
        # 連結グラフとして表現
        self.next_node = next_node
        self.is_root = True# 誰かの子でない
    
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
            self.next_node = layer
        else:
            self.next_node.append_child_to_tail(layer)

class DNNLinearLayer(DNNLayer):
    """
    行列積レイヤー(bias含まず)
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise, DNNLayerAttributes.PostChannelwise}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        super(DNNLinearLayer, self).__init__(name, DNNLayerType.Linear, DNNLinearLayer.ATTRIBUTES, parameters, weights)

class DNNBiasLayer(DNNLayer):
    """
    Channelwiseにウェイトを加算するレイヤー
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise, DNNLayerAttributes.PostChannelwise, DNNLayerAttributes.Channelwise, DNNLayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        super(DNNBiasLayer, self).__init__(name, DNNLayerType.Bias, DNNReluLayer.ATTRIBUTES, parameters, weights)

class DNNScaleLayer(DNNLayer):
    """
    Channelwiseにウェイトを乗算するレイヤー
    """
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise, DNNLayerAttributes.PostChannelwise, DNNLayerAttributes.Channelwise, DNNLayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]):
        super(DNNScaleLayer, self).__init__(name, DNNLayerType.Scale, DNNReluLayer.ATTRIBUTES, parameters, weights)

class DNNReluLayer(DNNLayer):
    """
    Reluレイヤー
    """
    # ElementwiseであればChannelwiseだが、このattribute定義がよいのかどうか？
    ATTRIBUTES = {DNNLayerAttributes.PostElementwise, DNNLayerAttributes.PostChannelwise, DNNLayerAttributes.Elementwise, DNNLayerAttributes.Channelwise, DNNLayerAttributes.Inplace}

    def __init__(self, name: str, parameters: Dict[str, object], weights: Dict[str, np.ndarray]=None):
        super(DNNReluLayer, self).__init__(name, DNNLayerType.Relu, DNNReluLayer.ATTRIBUTES, parameters, weights)

class DNNGraphNode:
    def __init__(self, name: str, layer: DNNLayer, bottoms: List[DNNVariable], tops: List[DNNVariable]):
        self.name = name
        self.layer = layer
        self.bottoms = bottoms
        self.tops = tops

class DNNGraph:
    def __init__(self, nodes: List[DNNGraphNode], inputs: List[DNNVariable], outputs: List[DNNVariable], batch_size: int):
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
                and len(cons_list) == 1\
                and DNNLayerAttributes.Elementwise in cons_first.layer.attributes:
                    # linearのうしろにreluをくっつける
                    prod.layer.append_child_to_tail(cons_first.layer)
                    # linearの出力がreluの出力になる
                    prod.tops[0] = cons_first.tops[0]
                    #後続レイヤーが持たないattributeを消す(これでいいのか？)
                    prod.layer.attributes &= cons_first.layer.attributes
                    # reluのノードは消える (同時に、linear-relu間の変数もなくなる)
                    self.graph.nodes.remove(cons_first)
                    break#グラフが変わったのでvariable_to_nodeをつくりなおす
                if prod is not None \
                and DNNLayerAttributes.PostChannelwise in prod.layer.attributes \
                and len(cons_list) == 1\
                and DNNLayerAttributes.Channelwise in cons_first.layer.attributes:
                    # linearのうしろにbiasをくっつける
                    prod.layer.append_child_to_tail(cons_first.layer)
                    # linearの出力がbiasの出力になる
                    prod.tops[0] = cons_first.tops[0]
                    #後続レイヤーが持たないattributeを消す(これでいいのか？)
                    prod.layer.attributes &= cons_first.layer.attributes
                    # biasのノードは消える (同時に、linear-bias間の変数もなくなる)
                    self.graph.nodes.remove(cons_first)
                    break#グラフが変わったのでvariable_to_nodeをつくりなおす
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
            