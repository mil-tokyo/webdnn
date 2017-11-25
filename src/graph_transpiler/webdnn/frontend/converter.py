from abc import abstractmethod
from collections import defaultdict
from typing import Callable, Dict, TypeVar, Generic

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable
from webdnn.util import console

T_OP = TypeVar('T_OP')

Handler = Callable[["Converter", T_OP], Operator]


class CyclicGraphError(Exception):
    pass


class Converter(Generic[T_OP]):
    """Converter()
    This class converts computation graph in other DNN library into WebDNN IR format.

    If you want to implement your custom converter, see :doc:`/tutorial/custom_operator/index`.
    """

    _handler_map = defaultdict(dict)  # type: Dict[str, Dict[str, Handler]]

    def __init__(self):
        self._variable_table = {}  # type: Dict[object, Variable]

    @abstractmethod
    def convert(self, *args, **kwargs) -> Graph:
        """convert(*args, **kwargs)
        Convert computation graph into WebDNN IR format. Arguments of this method is defined in each child class.

        Returns:
            Graph in WebDNN IR format
        """
        raise NotImplementedError

    @classmethod
    def register_handler(cls, key: str):
        """register_handler(key)
        Decorator to register operator converter handler.

        Args:
            key: operator type name. As default, it's the class name for each operator instance. you can change this
                 behavior by overriding :func:`~webdnn.converter.Converter.serialize_operator_type`.

        Returns:
            :
        """

        def decorator(handler: Handler):
            if key in cls._handler_map[cls.__name__]:
                console.warning(f"[{cls.__name__}] Converter Handler for '{key}' is already registered in {cls.__name__} and overwritten.")

            cls._handler_map[cls.__name__][key] = handler
            return handler

        return decorator

    def serialize_operator_type(self, operator: T_OP) -> str:
        """serialize_operator_type(operator)
        Serialize operators type in other DNN framework into strings

        Args:
            operator (Type): operator type in other DNN framework

        Returns:
            (str): serialized value
        """
        return operator.__class__.__name__

    def get_variable(self, key: object) -> Variable:
        """get_variable(key)
        Gets variable object corresponding to the key.

        Args:
            key (object): key

        Returns:
            (:class:`~webdnn.Variable`):variable object in WebDNN IR Format.
        """
        return self._variable_table[key]

    def set_variable(self, key: object, variable: Variable, overwrite: bool = False):
        """set_variable(key, variable)
        Stores variable object corresponding to the key.

        Args:
            key (object): key
            variable (:class:`~webdnn.Variable`): variable
            overwrite (bool): When False, if the key is already exist, KeyError is raised.
        """
        if not overwrite and key in self._variable_table:
            raise KeyError(f"Variable {key} already exists")
        self._variable_table[key] = variable

    def has_variable(self, key: object) -> bool:
        """has_variable(key)
        Check whether variable object corresponding to the key is generated or not.

        Args:
            key (object): key

        Returns:
            (bool): If :code:`True`, the key is contained.
        """
        return key in self._variable_table

    def _convert_operator(self, operator: T_OP):
        operator_key = self.serialize_operator_type(operator)
        if operator_key not in self._handler_map[self.__class__.__name__].keys():
            raise NotImplementedError(f"Operator '{operator_key}' is not handled any converter handlers.")

        self._handler_map[self.__class__.__name__][operator_key](self, operator)

        return None
