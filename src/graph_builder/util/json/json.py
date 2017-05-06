from abc import abstractmethod
from json import dump as original_dump, dumps as original_dumps, JSONEncoder


class SerializableMixin:
    @abstractmethod
    def _to_serializable_(self):
        raise NotImplementedError


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SerializableMixin):
            # noinspection PyProtectedMember
            return obj._to_serializable_()

        return JSONEncoder.default(self, obj)


def dump(*args, cls=CustomJSONEncoder, **kwargs):
    original_dump(*args, cls=cls, **kwargs)


def dumps(*args, cls=CustomJSONEncoder, **kwargs):
    original_dumps(*args, cls=cls, **kwargs)
