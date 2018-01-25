from abc import abstractmethod
from json import dump as original_dump, dumps as original_dumps, JSONEncoder
from typing import Union, List, Tuple

import numpy as np

# Serializable classes declared in json.JSONEncoder
# @see https://github.com/python/cpython/blob/e325608740bee161ca7fefd09463d63099efa1b8/Lib/json/encoder.py#L78-L94
JSONSerializable = Union[
    dict,
    List["JSONSerializable"],
    Tuple["JSONSerializable"],
    str,
    int, float,
    bool,
    None
]


class SerializableMixin:
    """
    Mixin class to support JSON serialization

    Instances which implement this mixin can be serialized by "webdnn.util.json.dump" (not python standard "json.dump" function)
    """

    @abstractmethod
    def _to_serializable_(self) -> JSONSerializable:
        """
        Convert this object to serializable object
        Returns:
            (:class:`~webdnn.util.json.JSONSerializable`) object which can be serialized by python standard "json.dump" function
        """
        raise NotImplementedError


class CustomJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder class to support SerializableMixin
    """

    def default(self, obj):
        if isinstance(obj, SerializableMixin):
            # noinspection PyProtectedMember
            return obj._to_serializable_()

        # Utility conversions to support numpy data object
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        if isinstance(obj, (np.int8, np.int16, np.int32, np.int64, np.int)):
            return int(obj)

        if isinstance(obj, (np.uint8, np.uint16, np.uint32, np.uint64, np.uint)):
            return int(obj)

        if isinstance(obj, (np.float16, np.float32, np.float64, np.float)):
            return float(obj)

        return super(CustomJSONEncoder, self).default(obj)


def dump(*args, cls=CustomJSONEncoder, **kwargs):
    """Wrapper function for standard "json.dump" with CustomJSONEncoder class"""
    return original_dump(*args, cls=cls, **kwargs)


def dumps(*args, cls=CustomJSONEncoder, **kwargs):
    """Wrapper function for standard "json.dumps" with CustomJSONEncoder class"""
    return original_dumps(*args, cls=cls, **kwargs)
