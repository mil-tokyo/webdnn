from typing import Dict, Any, Sequence, Union

from webdnn.backend.code_generator.injector import Tag, Injector
from webdnn.graph.variable import Variable
from webdnn.util import flags


class UniformInjector(Injector):
    def __init__(self):
        self.uniform_values = {}  # type: Dict[str, Dict[str, Any]]
        self.uniforms = {}
        self.samplers = []

    def register(self, data: Dict[str, Any]):
        self.uniform_values.update(data)

    def inject_tag(self, tag: Tag):
        if tag.name == "UNIFORM":
            typename, name = tag.args
            if name not in self.uniform_values:
                raise KeyError(f"Uniform '{name}' is requested, but it's not registered.")

            value = self.uniform_values[name]  # type: Union[float, int]
            injected_value_literal = ""

            if typename == "float":
                assert float(value) == value, f"Uniform value of 'float' must be float: value={value}"
                if float(value).is_integer():
                    injected_value_literal = f" = {float(value):.1f}"
                else:
                    injected_value_literal = f" = {float(value)}"

            elif typename == "int":
                assert int(value) == value, f"Uniform value of 'int' must be integer: value={value}"
                injected_value_literal = f" = {value}"

            elif typename == "vec2" or typename == "vec3" or typename == "vec4":
                assert isinstance(value, Sequence), f"Uniform value of '{typename}' must be sequence: type(value)={type(value)}"
                assert len(value) == int(typename[-1]), f"len(value) = {len(value)}, int(typename[-1]) = {int(typename[-1])}"
                injected_value_literal = f" = {typename}({', '.join([str(v) for v in value])})"

            elif typename == "ivec2" or typename == "ivec3" or typename == "ivec4":
                assert isinstance(value, Sequence), f"Uniform value of '{typename}' must be sequence: type(value)={type(value)}"
                assert len(value) == int(typename[-1]), f"len(value) = {len(value)}, int(typename[-1]) = {int(typename[-1])}"
                for i, v in enumerate(value):
                    assert int(v) == v, f"Uniform value of '{typename}' must be sequence of integer: value[{i}]={value[i]}"
                    injected_value_literal = f" = {typename}({', '.join([str(v) for v in value])})"

            elif typename == "sampler2D":
                assert isinstance(value, Variable), f"Uniform value for sampler2D must be Variable instance: type(value)={type(value)}"
                variable = value  # type: Variable
                value = len(self.samplers)
                self.samplers.append({
                    "variable_name": variable.name,
                    "value": value
                })

            else:
                raise TypeError(f"Unknown uniform type: {typename}")

            if flags.optimize.OPTIMIZE and flags.optimize.EXTRACT_UNIFORM_LITERAL and injected_value_literal != "":
                return f"{typename} {name}{injected_value_literal}"

            else:
                self.uniforms[name] = {
                    "type": typename,
                    "value": value
                }
                return f"uniform {typename} {name}"

        else:
            return tag.original
