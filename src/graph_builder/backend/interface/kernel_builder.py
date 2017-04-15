# -*- coding:utf-8 -*-
from graph_builder.graph import Graph


class GraphDescriptorGenerator:
    graph: Graph

    def __init__(self, graph: Graph):
        self.graph = graph

    def generate(self):
        raise NotImplementedError
