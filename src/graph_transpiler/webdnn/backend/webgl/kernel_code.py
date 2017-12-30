import hashlib
from abc import ABCMeta
from enum import Enum, auto
from typing import Sequence, Union, Any, Hashable, Dict, List, NamedTuple

from webdnn.graph.placeholder import Placeholder
from webdnn.graph.variable import Variable


class Type(Enum):
    Int = auto()
    Float = auto()
    Ivec = auto()
    Vec = auto()
    Sampler2D = auto()

    def get_name(self, value=None):
        if self == Type.Int:
            return "int"

        if self == Type.Float:
            return "float"

        if self == Type.Ivec:
            assert 2 <= len(value) <= 4
            return f"ivec{len(value)}"

        if self == Type.Vec:
            assert 2 <= len(value) <= 4
            return f"vec{len(value)}"

        if self == Type.Sampler2D:
            return f"sampler2D"

        raise NotImplementedError

    def literalize(self, value):
        if self == Type.Ivec:
            value = [v.expression if isinstance(v, IntExpressionNode) else v for v in value]
            assert 2 <= len(value) <= 4 and all(int(v) == v for v in value)
            return f"ivec{len(value)}({','.join(str(int(v)) for v in value)})"

        if self == Type.Vec:
            value = [v.expression if isinstance(v, FloatExpressionNode) else v for v in value]
            assert 2 <= len(value) <= 4 and all(float(v) == v for v in value)
            return f"vec{len(value)}({','.join(str(float(v)) for v in value)})"

        if self == Type.Int:
            return str(int(value))

        if self == Type.Float:
            return str(float(value))

        raise NotImplementedError


class Node(metaclass=ABCMeta):
    def __call__(self) -> Union[int, float, str, Placeholder, "Node", Sequence[Union[int, float, str, Placeholder, "Node"]]]:
        raise NotImplementedError


Expression = Union[int, float, str, Placeholder, Node, Sequence[Union[int, float, str, Placeholder, Node]]]


class StatementNode(Node):
    def __init__(self, expression: Expression = ""):
        self.expression = expression

    def __call__(self):
        return [self.expression, ";"]


class ExpressionNode(Node):
    def __init__(self, expression: Expression = ""):
        self.expression = expression

    def __call__(self):
        return ["(", self.expression, ")"]


class IntExpressionNode(ExpressionNode):
    def __call__(self):
        # noinspection PyTypeChecker
        if Placeholder.check_resolved(self.expression):
            return ["(", int(self.expression), ")"]

        else:
            return ["(int(", self.expression, "))"]


class FloatExpressionNode(ExpressionNode):
    def __call__(self):
        # noinspection PyTypeChecker
        if Placeholder.check_resolved(self.expression):
            return ["(", float(self.expression), ")"]

        else:
            return ["(float(", self.expression, "))"]


class GlobalDeclarationNode(StatementNode):
    def __init__(self, type: Type, name: str, value: Any = None, attributes: List[str] = None, with_value: bool = False):
        super(GlobalDeclarationNode, self).__init__()
        self.type = type
        self.varname = name
        self.value = value
        self.attributes = [] if attributes is None else attributes
        self.with_value = with_value

    def __call__(self):
        statement = ""

        if self.with_value and (self.value is not None):
            statement += "const "

        if len(self.attributes) > 0:
            statement += f"{' '.join(self.attributes)} "

        statement += f"{self.type.get_name(self.value)} {self.varname}"

        if self.with_value and (self.value is not None):
            statement += f" = {self.type.literalize(self.value)}"

        statement += ";\n"

        return statement


class UniformDeclarationNode(GlobalDeclarationNode):
    def __init__(self, type: Type, name: str, value: Any = None):
        super(UniformDeclarationNode, self).__init__(type, name, value=value, attributes=["uniform"])


class UnresolvedUniform(NamedTuple):
    varname: str
    placeholder: Placeholder


class KernelCode:
    def __init__(self, fragments: Sequence[Any], name=None):
        self.fragments = fragments
        self._varnames = {}  # type: Dict[int, str]
        self._uniforms = {}
        self._samplers = {}
        self._declared_vars = []
        self._name = None  # type: str
        self._name_prefix = name

    @property
    def name(self):
        return self._name

    @property
    def samplers(self):
        return list(self._samplers.values())

    @property
    def uniforms(self):
        return dict(self._uniforms)

    def _initialize_context(self):
        self._varnames = {}
        self._uniforms = {}
        self._samplers = {}
        self._declared_vars = []
        self._name = None
        self._unresolved_uniform_list = {}  # type: Dict[Placeholder, UnresolvedUniform]

    def get_varname(self, obj: Hashable):
        h = hash(obj)
        if h not in self._varnames:
            self._varnames[h] = f"v{len(self._varnames)}"

        return self._varnames[h]

    def register_sampler(self, node: UniformDeclarationNode):
        if node.value not in self._samplers:
            sampler_id = len(self._samplers)
            self._samplers[node.value] = {
                "variable_name": node.value.name,
                "value": sampler_id
            }
            self._uniforms[node.varname] = {
                "type": node.type.get_name(node.value),
                "value": sampler_id
            }

    def register_uniform(self, node: UniformDeclarationNode):
        self._uniforms[node.varname] = {
            "type": node.type.get_name(node.value),
            "value": node.value
        }

    def generate(self) -> str:
        from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble

        self._initialize_context()
        que = list(self.fragments)

        head = FragmentShaderPreamble
        body = ""

        while len(que) > 0:
            node = que.pop(0)
            if isinstance(node, Node):
                if isinstance(node, GlobalDeclarationNode):
                    if hash((node.type, node.value)) in self._declared_vars:
                        continue
                    self._declared_vars.append(hash((node.type, node.value)))

                    if "uniform" in node.attributes:
                        node = node  # type: UniformDeclarationNode
                        if node.type == Type.Sampler2D:
                            self.register_sampler(node)

                        else:
                            self.register_uniform(node)

                    head += node()
                    continue

                if isinstance(node, StatementNode):
                    que = [node()] + que
                    continue

                if isinstance(node, ExpressionNode):
                    que = [node()] + que
                    continue

            if isinstance(node, Variable):
                varname = self.get_varname(node)
                que = [UniformDeclarationNode(Type.Sampler2D, varname, value=node), varname] + que
                continue

            if not isinstance(node, str) and isinstance(node, Sequence):
                if len(node) == 0:
                    continue

                if all(isinstance(v, (int, IntExpressionNode)) for v in node):
                    if len(node) > 4:
                        raise NotImplementedError(f"Length of sequence of int must be 2, 3, or 4: (len(sequence)) = {len(node)}")

                    node = tuple(node)
                    varname = self.get_varname((Type.Ivec, node))
                    que = [GlobalDeclarationNode(Type.Ivec, varname, value=node, with_value=True), varname] + que
                    continue

                if all(isinstance(v, (float, FloatExpressionNode)) for v in node):
                    if len(node) > 4:
                        raise NotImplementedError(f"Length of sequence of float must be 2, 3, or 4: (len(sequence)) = {len(node)}")

                    node = tuple(node)
                    varname = self.get_varname((Type.Vec, node))
                    que = [GlobalDeclarationNode(Type.Vec, varname, value=node, with_value=True), varname] + que
                    continue

                que = list(node) + que
                continue

            if isinstance(node, (int, float, str)):
                body += str(node)
                continue

            if isinstance(node, Placeholder):
                if Placeholder.check_resolved(node):
                    body += str(node.value)

                else:
                    if node in self._unresolved_uniform_list:
                        varname = self._unresolved_uniform_list[node].varname

                    else:
                        varname = self.get_varname(node)
                        self._unresolved_uniform_list[node] = UnresolvedUniform(varname=varname, placeholder=node)

                    que = [UniformDeclarationNode(Type.Int, varname), varname] + que

                continue

            raise NotImplementedError(node)

        source = head + body
        self._name = f"{hashlib.sha224(source.encode('utf-8')).hexdigest()}"
        if self._name_prefix is not None:
            self._name = f"{self._name_prefix}_{self._name}"
        return source
