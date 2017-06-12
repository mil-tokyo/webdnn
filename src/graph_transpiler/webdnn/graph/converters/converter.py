import warnings
from abc import abstractmethod
from typing import Callable, Dict, Iterable, TypeVar, Generic, Type, List
from collections import defaultdict

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable

T_OP = TypeVar('T_OP')


class Converter(Generic[T_OP]):
    """Converter base class

    This class converts computation graph in some DNN library into WebDNN IR format.

    To use this class, you should implement 2 methods

    - :func:`~webdnn.converter.Converter.convert_core`
    - :func:`~webdnn.converter.Converter.convert_variable_core`

    Also you have to implement ConvertHandler for each operator (Please see  :func:`~webdnn.converter.Converter.register_handler`).
    """

    ConvertHandler = Callable[["Converter", T_OP], Operator]

    """
    For each concrete Converter
    """
    _handler_map = defaultdict(dict)  # type: Dict[str, Dict[str, ConvertHandler]]
    _variable_table = defaultdict(dict)  # type: Dict[str, Dict[object, Variable]]

    @abstractmethod
    def convert_core(self, *args, **kwargs) -> Graph:
        """Convert computation graph into WebDNN IR format.

        This is main routine of converter. You need to implement follow operations.

        1. Traverse given computation graph and for each operator, call
            :func:`~webdnn.converter.Converter.convert_operator` with the operator and variables.
            This method converts the operator in IR format and build computation graph around this operator.

        2. Build and return computation graph. This procedure can be implemented simply as follows::

            inputs = [self.convert_variable(v) for v in graph_in_other_library_format.inputs]
            outputs = [self.convert_variable(v) for v in graph_in_other_library_format.outputs]

            return webdnn.graph.graph.Graph(inputs, outputs)

        Returns:
            Graph in WebDNN IR format
        """
        raise NotImplementedError

    @abstractmethod
    def serialize_operator_type(self, operator: T_OP) -> str:
        raise NotImplementedError

    def get_variable(self, key: object) -> Variable:
        """Gets variable object corresponding to the key.

        Returns:
            variable object in WebDNN IR Format.
        """
        return self._variable_table[self.__class__.__name__][key]

    def set_variable(self, key: object, variable: Variable):
        """Stores variable object corresponding to the key.

        """
        if key in self._variable_table[self.__class__.__name__]:
            raise ValueError(f"Variable {key} already exists")
        self._variable_table[self.__class__.__name__][key] = variable

    @classmethod
    def register_handler(cls, OperatorClass: str):
        """Decorator to register operator converter handler

        You need to implement handlers for all operators you want to supports. Each handler is consisted as follows:

        1. Call :func:`~webdnn.converter.Converter.convert_variable` for each input and output variables.
            This method converts the variable in IR format.

        2. Connect computation graph.

            :func:`~webdnn.converter.Converter.convert_variable` returns same object reference when the first argument is same.
            For example, considering follows sequential graph.

            .. code-block:: text

                v1 -[op1]-> v2 -[op2]-> v3

            In this case, `op1.outputs[0]` and `op2.inputs[0]` is same object (`v2`), so `convert_variable(op1.outputs[0])` and
            `convert_variable(op2.inputs[0])` return same variable object reference. Therefore convert routine can be written simply as
            follows::

            @MyConverter.register_handler(MyCustomOperator)
            def my_custom_handler(converter: MyConverter, op: MyCustomOperator, inputs: List[Variable], outputs: List[Variable]):
                op = webdnn.graph.operators.SomeWebDNNOperator(op.some_hyper_parameter)
                x = self.convert_variable(inputs[0], OrderNHWC)
                y = self.convert_variable(outputs[0], OrderNHWC)

                y_dummy = op(x)
                op.replace_output(y_dummy, y)

        Args:
            OperatorClass: operator class

        .. code-block:: python

        """

        def decorator(handler: cls.ConvertHandler):
            key = OperatorClass
            if key in cls._handler_map:
                warnings.warn(
                    f"Converter Handler for '{OperatorClass}' is already registered in {cls.__name__} and overwritten.")

            cls._handler_map[cls.__name__][key] = handler

        return decorator

    def convert(self, *args, **kwargs) -> Graph:
        return self.convert_core(*args, **kwargs)

    def convert_operator(self, operator: T_OP):
        operator_key = self.serialize_operator_type(operator)
        if operator_key not in self._handler_map[self.__class__.__name__].keys():
            raise NotImplementedError(f"Operator '{operator_key}' is not handled any converter handlers.")

        self._handler_map[self.__class__.__name__][operator_key](self, operator)

        return None
