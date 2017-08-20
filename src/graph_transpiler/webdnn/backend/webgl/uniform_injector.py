from typing import Dict, Any, List

from webdnn.backend.code_generator.injector import Tag, Injector
from webdnn.graph.variable import Variable


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

            value = self.uniform_values[name]
            if typename == "float":
                # noinspection PyTypeChecker
                assert float(value) == value, f"Uniform value of 'float' must be float: value={value}"

            elif typename == "int":
                # noinspection PyTypeChecker
                assert int(value) == value, f"Uniform value of 'int' must be integer: value={value}"

            elif typename == "vec2" or typename == "vec3" or typename == "vec4":
                assert isinstance(value, List), f"Uniform value of '{typename}' must be list: type(value)={type(value)}"

            elif typename == "ivec2" or typename == "ivec3" or typename == "ivec4":
                assert isinstance(value, List), f"Uniform value of '{typename}' must be list: type(value)={type(value)}"
                for i, v in enumerate(value):
                    assert int(v) == v, f"Uniform value of '{typename}' must be list of integer: value[{i}]={value[i]}"

            elif typename == "sampler2D":
                assert isinstance(value, Variable), f"Uniform value for sampler2D must be Variable instance: type(value)={type(value)}"
                variable = value  # type: Variable
                value = len(self.samplers)
                self.samplers.append({
                    "uniform_name": "name",
                    "variable_name": variable.name,
                    "value": value
                })

            else:
                raise TypeError(f"Unknown uniform type: {typename}")

            self.uniforms[name] = {
                "type": typename,
                "value": value
            }

            return f"uniform {typename} {name}"

        else:
            return tag.original
