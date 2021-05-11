import onnx


def get_attr_int(op: onnx.NodeProto, name, default=None):
    for attr in op.attribute:
        if attr.name == name:
            return attr.i
    return default


def get_attr_ints(op: onnx.NodeProto, name, default=None):
    for attr in op.attribute:
        if attr.name == name:
            return list(attr.ints)
    return default


def get_attr_float(op: onnx.NodeProto, name, default=None):
    for attr in op.attribute:
        if attr.name == name:
            return attr.f
    return default
