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
    def __init__(self, name: str, layer_type: DNNLayerType, attributes: Set[DNNLayerAttributes], parameters: Dict[str, object], weights: Dict[str, np.ndarray], temporary_variables: List[DNNVariable], children):
        self.name = name
        self.layer_type = layer_type
        self.attributes = attributes
        self.parameters = parameters
        self.weights = weights
        self.temporary_variables = temporary_variables
        self.children = children
    
    def iterate_self_and_children(self):
        yield self
        for child in self.children:
            yield child


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

