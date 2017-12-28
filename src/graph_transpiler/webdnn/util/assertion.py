from typing import Any, Type, Union, Sequence

from webdnn.util import flags, console


class UnexpectedAndPleaseReportError(NotImplementedError):
    def __init__(self, message: str = ""):
        message = f"Unexpected error is occurred. Please report this error with stack trace to " \
                  f"https://github.com/mil-tokyo/webdnn/issues/new: \n" \
                  f"  (original message)={message}"
        super(UnexpectedAndPleaseReportError, self).__init__(message)


def assert_equal(a, b, message: str = ""):
    if a != b:
        raise AssertionError(f"{message}{'' if message == '' else ': '}{a} != {b}")


def assert_sequence_type(value: Any, correct_type: Union[Type, Sequence[Type]],
                         auto_fix: bool = None, message: str = None, warning=True):
    """
    Assert type of each element in list.

    Args:
        value (Any): The sequence
        correct_type (Type): correct type for each element.
        auto_fix (bool, Optional): If True, the type is automatically fixed if possible. As default, the value is depend on the flag
            :obj:`~webdnn.flags.FORCE_TYPE_CHECK`
        message (str, Optional): The error message
        warning (bool, Optional): If True, warning message is displayed. Default is True.

    Returns:

    """
    if not isinstance(correct_type, Sequence):
        correct_type = (correct_type,)

    if message is None:
        message = f"""
Assertion failed. Value must be an sequence of {correct_type[0].__name__}"""

    if auto_fix is None:
        auto_fix = not flags.FORCE_TYPE_CHECK

    # check "value" is list instance
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"""
{message}:
    (value) = {value}
    (type of value) = {type(value)}
""")

    tmp = list(value)

    # check type of each element
    for i, v in enumerate(value):
        if isinstance(v, correct_type):
            continue

        error_message = f"""
{message}
    (value) = {value}
    (type of value[{i}]) = {type(v)}"""
        if auto_fix:
            tmp[i] = correct_type[0](v)

        else:
            raise TypeError(error_message)

        if warning:
            console.warning(error_message)
            warning = False

    if auto_fix:
        if isinstance(value, list):
            value = list(tmp)

        elif isinstance(value, tuple):
            value = tuple(tmp)

        else:
            raise NotImplementedError

    return value
