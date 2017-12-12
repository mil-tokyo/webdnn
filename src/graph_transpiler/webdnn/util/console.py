import shutil
import sys
import warnings
from typing import Any, Type, Optional

from webdnn.util import flags

ESC = "\x1b"


class Color:
    Black = 0
    Red = 1
    Green = 2
    Yellow = 3
    Blue = 4
    Magenta = 5
    Cyan = 6
    White = 7


def colorize(text: str, color: int, bright: bool = False):
    if sys.platform == 'win32':
        return text
    else:
        return f"{ESC}[{'1' if bright else '0'};3{color}m{text}{ESC}[0;39m"


def warning(message: str, category: Optional[Type[Warning]] = Warning):
    warnings.warn(message, category)


def error(*texts: Any):
    stderr(colorize("".join(map(str, texts)), Color.Red))


def debug(*texts: Any):
    if flags.DEBUG:
        stderr(colorize("[DEBUG]", Color.Blue) + " " + "".join(map(str, texts)))


def info(*texts: Any):
    return colorize("".join(map(str, texts)), Color.Green)


def get_size():
    return shutil.get_terminal_size()


def get_width():
    return get_size()[0]


def get_height():
    return get_size()[1]


def stderr(*texts: Any):
    sys.stderr.write("".join(map(str, texts)) + "\n")
