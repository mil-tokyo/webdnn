import hashlib

from graph_builder.graph import Operator
from graph_builder.graph.operators.compose import VariableAlias


def get_input(op: Operator, name: str):
    v = op.inputs[name]
    return v.original if isinstance(v, VariableAlias) else v


def get_output(op: Operator, name: str):
    v = op.outputs[name]
    return v.original if isinstance(v, VariableAlias) else v


def add_canonical_suffix(base_name: str, source: str):
    return f"{base_name}_{hashlib.sha224(source.encode('utf-8')).hexdigest()}"
