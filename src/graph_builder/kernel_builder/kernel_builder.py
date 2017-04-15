# -*- coding:utf-8 -*-
from ..graph import Graph


class KernelBuilder:
    def __init__(self, graph: Graph):
        self.graph = graph

    def build(self):
        raise NotImplementedError
