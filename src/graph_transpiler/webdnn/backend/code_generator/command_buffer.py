from typing import List, Tuple

from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.util import flags


class CommandBuffer:
    def __init__(self, buffer_injector: BufferInjector):
        self.codes = []  # type: List[Tuple]
        self.buffer_injector = buffer_injector
        self._unique_counter = 0

    def _generate_unique_name(self, prefix=""):
        self._unique_counter += 1
        return prefix + str(self._unique_counter)

    def declare(self, varname: str, typename: str, initial_value: str = None, const: bool = False):
        """Declare new variable"""
        self.codes.append(("declare", typename, varname, initial_value, const))

    def load(self, varname: str, value: any, typename: str = None, const: bool = False):
        """Load data from buffer (Internally, %%LOAD_BUFFER%% is called)"""
        buffer_key = self._generate_unique_name()
        self._unique_counter += 1

        if flags.DEBUG:
            self.comment(f"load: {value}")

        self.codes.append(("load", typename, varname, buffer_key, const))
        self.buffer_injector.register({
            buffer_key: value
        })

    def exec(self, expression: str):
        """Execute any expression"""
        self.codes.append(("exec", expression))

    def enterFor(self, counter: str, initial_val: str, max_val: str, step_value: str):
        """Enter for-loop"""
        self.codes.append(("enterFor", counter, initial_val, max_val, step_value))

    def exitFor(self):
        """Exit for-loop"""
        self.codes.append(("exitFor",))

    def enterBlockScope(self):
        """Enter new block scope. All declared variable in this scope has no effect for outside of the scope."""
        self.codes.append(("enterBlockScope",))

    def exitBlockScope(self):
        """Exit block scope."""
        self.codes.append(("exitBlockScope",))

    def comment(self, text):
        """Add comment."""
        self.codes.append(("comment", text))
