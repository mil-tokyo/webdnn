from abc import abstractmethod
from json import dump as original_dump, dumps as original_dumps, JSONEncoder

import numpy as np


class SerializableMixin:
    @abstractmethod
    def _to_serializable_(self):
        raise NotImplementedError


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SerializableMixin):
            # noinspection PyProtectedMember
            return obj._to_serializable_()

        if isinstance(obj, np.int64) or isinstance(obj, np.int32) or isinstance(obj, np.int16) or isinstance(obj, np.int8) or \
            isinstance(obj, np.uint32) or isinstance(obj, np.uint16) or isinstance(obj, np.uint8):
            # noinspection PyTypeChecker
            return int(obj)

        if isinstance(obj, np.float64) or isinstance(obj, np.float32) or isinstance(obj, np.float16):
            # noinspection PyTypeChecker
            return float(obj)

        return JSONEncoder.default(self, obj)


def dump(*args, cls=CustomJSONEncoder, **kwargs):
    return original_dump(*args, cls=cls, **kwargs)


def dumps(*args, cls=CustomJSONEncoder, **kwargs):
    return original_dumps(*args, cls=cls, **kwargs)
