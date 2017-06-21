from abc import abstractmethod
from collections import defaultdict
from typing import Callable, Dict, TypeVar, Generic

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.variable import Variable
from webdnn.util import console

T_OP = TypeVar('T_OP')


class Converter(Generic[T_OP]):
    """Converter base class

    This class converts computation graph in some DNN library into WebDNN IR format.

    To use this class, you should implement :func:`~webdnn.converter.Converter.convert_core` and
    convert handler for each operator (Please see :func:`~webdnn.converter.Converter.register_handler`).
    """

    """
    For each concrete Converter
    """
    _handler_map = defaultdict(dict)  # type: Dict[str, Dict[str, Callable[["Converter", T_OP], Operator]]]
    _variable_table = defaultdict(dict)  # type: Dict[str, Dict[object, Variable]]

    @abstractmethod
    def convert_core(self, *args, **kwargs) -> Graph:
        """Convert computation graph into WebDNN IR format.

        This is main routine of converter. You need to implement follow operations.

        1. Traverse given computation graph and for each operator, call
            :func:`~webdnn.converter.Converter.convert_operator` with the operator and variables.
            This method converts the operator in IR format and build computation graph around this operator.

        2. Build and return computation graph. This procedure can be implemented simply like follows::

        Returns:
            Graph in WebDNN IR format
        """
        raise NotImplementedError

    @classmethod
    def register_handler(cls, key: str):
        """Decorator to register operator converter handler

        You need to implement handlers for all operators you want to supports. Each handler is consisted as follows:

        1. Call :func:`~webdnn.converter.Converter.convert_variable` for each input and output variables.
            This method converts the variable in IR format.

        2. Connect computation graph.

            For example, considering follows sequential graph in framework A. let op1 and op2 be instances of
            `A.SomeOperator`

            .. code-block:: text

                v1 -[op1]-> v2 -[op2]-> v3

            Converter handler can be implemented as follows::

            @A_Converter.register_handler("SomeOperator")
            def _handler(converter: A_Converter, op_A: A.SomeOperator):
                # convert operator into WebDNN IR
                op_webdnn = webdnn.graph.operators.SomeOperator(op_A.some_hyper_parameter)

                # connect input variable
                if converter.has_variable(op_A.inputs[0]):
                    x = self.get_variable(op_A.inputs[0])

                else:
                    x = webdnn.graph.variable.Variable(op_A.inputs[0].shape, OrderNHWC)
                    self.set_variable(op_A.inputs[0], x)

                # connect output variable
                if converter.has_variable(op_A.outputs[0]):
                    y = self.get_variable(op_A.outputs[0])
                    y_dummy = op_WebDNN(x)
                    op.replace_output(y_dummy, y)

                else:
                    y = op_WebDNN(x)
                    self.set_variable(op.outputs[0], y)

        Args:
            key: operator type name. As default, it's the class name for each operator instance. you can change this
                 behavior by overriding :func:`~webdnn.converter.Converter.serialize_operator_type`.
        """

        def decorator(handler: Callable[["Converter", T_OP], Operator]):
            if key in cls._handler_map[cls.__name__]:
                console.warning(f"[f{cls.__name__}] Converter Handler for '{key}' is already registered in {cls.__name__} and overwritten.")

            cls._handler_map[cls.__name__][key] = handler

        return decorator

    def serialize_operator_type(self, operator: T_OP) -> str:
        return operator.__class__.__name__

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

    def has_variable(self, key: object) -> bool:
        """Check whether variable object corresponding to the key is generated or not.

        """
        return key in self._variable_table[self.__class__.__name__]

    def convert(self, *args, **kwargs) -> Graph:
        return self.convert_core(*args, **kwargs)

    def convert_operator(self, operator: T_OP):
        operator_key = self.serialize_operator_type(operator)
        if operator_key not in self._handler_map[self.__class__.__name__].keys():
            raise NotImplementedError(f"Operator '{operator_key}' is not handled any converter handlers.")

        self._handler_map[self.__class__.__name__][operator_key](self, operator)

        return None
