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
    Relu = auto()

class DNNLayerAttributes(Enum):
    Inplace = auto()
    Elementwise = auto()
    Channelwise = auto()
    PostElementwise = auto()
    PostChannelwise = auto()

class DNNVariableAttributes(Enum):
    Input = auto()
    Output = auto()
    Temporary = auto()

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
    def __init__(self, name: str, layer_type: DNNLayerType, attributes: Set[DNNLayerAttributes], parameters: Dict[str, object], weights: Dict[str, np.ndarray], temporary_variables: List[DNNVariable], next_node):
        self.name = name
        self.layer_type = layer_type
        self.attributes = attributes
        self.parameters = parameters
        self.weights = weights
        self.temporary_variables = temporary_variables
        # 今の所、1出力レイヤーの後ろに1入力1出力レイヤーをくっつけるだけの機能
        # 連結グラフとして表現
        self.next_node = next_node
    
    def iterate_self_and_children(self):
        yield self
        if self.next_node is not None:
            for child in self.next_node.iterate_self_and_children():
                yield child

    def append_child_to_tail(self, layer):
        """
        連結グラフの末尾にレイヤーをくっつける
        """
        if self.next_node is None:
            self.next_node = layer
        else:
            self.next_node.append_child_to_tail(layer)

class DNNGraphNode:
    def __init__(self, name: str, layer: DNNLayer, bottoms: List[DNNVariable], tops: List[DNNVariable]):
        self.name = name
        self.layer = layer
        self.bottoms = bottoms
        self.tops = tops

class DNNGraph:
    def __init__(self, nodes: List[DNNGraphNode], inputs: List[DNNVariable], outputs: List[DNNVariable]):
        self.nodes = nodes
        self.inputs = inputs
        self.outputs = outputs

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
                and prod.layer.layer_type == DNNLayerType.Linear \
                and len(cons_list) == 1\
                and cons_first.layer.layer_type == DNNLayerType.Relu:
                    # linearのうしろにreluをくっつける
                    prod.layer.append_child_to_tail(cons_first.layer)
                    # linearの出力がreluの出力になる
                    prod.tops[0] = cons_first.tops[0]
                    # reluのノードは消える (同時に、linear-relu間の変数もなくなる)
                    self.graph.nodes.remove(cons_first)
                    break
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
            