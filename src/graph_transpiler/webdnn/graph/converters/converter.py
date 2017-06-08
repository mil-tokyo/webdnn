import warnings
from abc import abstractmethod
from typing import Callable, Dict, Iterable, TypeVar, Generic, Type, List

from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable

T_OP = TypeVar('T_OP')
T_VA = TypeVar('T_VA')


class Converter(Generic[T_OP, T_VA]):
    """Converter base class

    This class converts computation graph in some DNN library into WebDNN IR format.

    To use this class, you should implement 2 methods

    - :func:`~webdnn.converter.Converter.convert_core`
    - :func:`~webdnn.converter.Converter.convert_variable_core`

    Also you have to implement ConvertHandler for each operator (Please see  :func:`~webdnn.converter.Converter.register_handler`).
    """

    _handler_map = {}  # type: Dict[Type[T_OP], ConvertHandler]
    _converted_variables = {}  # type: Dict[T_VA, Variable]

    ConvertHandler = Callable[["Converter", T_OP, Iterable[T_VA], Iterable[T_VA]], Operator]

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
    def convert_variable_core(self, variable: T_VA, order: Order = None) -> Variable:
        """Convert variable object into WebDNN IR Format.

        Args:
            variable: variable object in other DNN library
            order: order

        Returns:
            variable object in WebDNN IR Format.
        """
        raise NotImplementedError

    @classmethod
    def register_handler(cls, OperatorClass: Type[T_OP]):
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
            if OperatorClass in cls._handler_map:
                warnings.warn(f"Converter Handler for '{OperatorClass.__name__}' is already registered in {cls.__name__} and overwritten.")

            cls._handler_map[OperatorClass] = handler

        return decorator

    def convert(self, *args, **kwargs) -> Graph:
        self._converted_variables = {}
        return self.convert_core(*args, **kwargs)

    def convert_operator(self, operator: T_OP, inputs: Iterable[T_VA], outputs: Iterable[T_VA]):
        matched_classes = []  # type: List[str]
        for klass in self._handler_map.keys():
            if not isinstance(operator, klass):
                continue

            matched_classes.append(klass.__name__)
            if len(matched_classes) == 1:
                self._handler_map[klass](self, operator, inputs, outputs)

        if len(matched_classes) == 0:
            raise NotImplementedError(f"Operator '{operator.__class__.__name__}' is not handled any converter handlers.")

        if len(matched_classes) > 1:
            raise TypeError(f"Operator '{operator.__class__.__name__}' is handled more than one converter handlers:"
                            + f" [{','.join(matched_classes)}]")

        return None

    def convert_variable(self, variable: T_VA, order: Order = None) -> Variable:
        if variable in self._converted_variables:
            return self._converted_variables[variable]

        converted_variable = self.convert_variable_core(variable, order)
        self._converted_variables[variable] = converted_variable

        return converted_variable
