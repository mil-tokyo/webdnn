# -*- coding:utf-8 -*-
from graph_builder.util import json


class GraphDescriptor(json.SerializableMixin):
    def _to_serializable_(self):
        raise NotImplementedError
