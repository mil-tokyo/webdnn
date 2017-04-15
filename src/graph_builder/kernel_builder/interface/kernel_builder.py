# -*- coding:utf-8 -*-
from graph_builder.graph import Graph


class KernelBuilder:
    graph: Graph

    def __init__(self, graph: Graph):
        self.graph = graph

    def build(self):
        raise NotImplementedError
