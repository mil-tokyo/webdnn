from typing import Dict, Any

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
                pass

            elif typename == "int":
                pass

            elif typename == "vec2":
                pass

            elif typename == "ivec2":
                pass

            elif typename == "vec4":
                pass

            elif typename == "ivec4":
                pass

            elif typename == "sampler2D":
                assert isinstance(value, Variable), f"Value for sampler2D must be Variable instance: type(value)={type(value)}"
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
