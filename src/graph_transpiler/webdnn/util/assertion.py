class UnexpectedAndPleaseReportError(NotImplementedError):
    def __init__(self, message):
        message = f"Unexpected error is occurred. Please report this error with stack trace to " \
                  f"https://github.com/mil-tokyo/webdnn/issues/new: \n" \
                  f"  (original message)={message}"
        super(UnexpectedAndPleaseReportError, self).__init__(message)


def assert_equal(a, b, message: str = ""):
    if a != b:
        raise AssertionError(f"{message}{'' if message == '' else ': '}{a} != {b}")
