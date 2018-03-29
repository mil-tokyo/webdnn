import sys
import os
import ast
from typing import Dict
from webdnn.util import console


def get_python_ast(path) -> ast.Module:
    with open(path) as f:
        source = f.read()
    return ast.parse(source)


def get_functiondef(p_ast: ast.Module) -> ast.FunctionDef:
    for node in p_ast.body:
        if isinstance(node, ast.FunctionDef):
            return node
    raise ValueError


SCALAR_TYPES = ["int", "float"]


class FunctionVisitor(ast.NodeVisitor):
    var_types: Dict[str, str]

    def __init__(self):
        self.var_types = {}
        self.var_strides = {}
        self.c_src = ""

    def visit(self, node: ast.AST):
        console.debug(f"visit {node}")
        return super().visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # def SquareLayer(shape, pos, array1_shape, array1):
        self.var_types["shape"] = "tuple"
        self.var_types["pos"] = "tuple"
        self.var_types["array1_shape"] = "tuple"
        self.var_types["array1"] = "array"
        self.var_strides["array1"] = ["(array1_shape[1])", "1"]
        self.c_src += "float %%FUNC_NAME%%_element(const int* shape, const int* pos, const int* array1_shape, const float* array1) {\n"
        for body_node in node.body:
            self.visit(body_node)
        self.c_src += "}\n"

    def visit_Assign(self, node: ast.Assign):
        assert len(node.targets) == 1, "multiple assignment not implemented"
        target_id = node.targets[0].id
        c_src_stack = self.c_src
        self.c_src = ""
        rhs_type = self.visit(node.value)
        c_src_value = self.c_src
        self.c_src = c_src_stack
        if target_id in self.var_types:
            assert self.var_types[target_id] == rhs_type, "re-assignment of different type"
        else:
            assert rhs_type in ["int", "float"]
            self.var_types[target_id] = rhs_type
            self.c_src += f"{rhs_type} {target_id};\n"
            console.debug(f"assignment to {target_id} type {rhs_type}")
        self.c_src += f"{target_id} = {c_src_value};\n"

    def visit_Subscript(self, node: ast.Subscript):
        # pos[0]
        assert isinstance(node.value, ast.Name)
        value_id = node.value.id
        value_type = self.var_types[value_id]
        assert value_type in ["tuple", "array"]
        assert isinstance(node.slice, ast.Index)
        slice_value = node.slice.value
        self.c_src += f"{value_id}["
        if value_type == "tuple":
            # slice value must be int
            assert self.visit(slice_value) == "int", "tuple index must be int"
            self.c_src += "]"
            return "int"
        elif value_type == "array":
            assert isinstance(slice_value, ast.Tuple)
            strides = self.var_strides[value_id]
            for dim, elt in enumerate(slice_value.elts):
                c_src_stack = self.c_src
                self.c_src = ""
                assert self.visit(elt) == "int", "array index must be tuple of int"
                c_src_value = self.c_src
                self.c_src = c_src_stack
                if dim > 0:
                    self.c_src += " + "
                self.c_src += f"({c_src_value}) * {strides[dim]}"
            self.c_src += "]"
            return "float"

    def visit_Num(self, node: ast.Num):
        n = node.n
        self.c_src += str(n)
        if isinstance(n, int):
            return "int"
        elif isinstance(n, float):
            return "float"
        else:
            raise NotImplementedError("num is not int or float")

    def visit_Name(self, node: ast.Name):
        # this must not called when lhs of assignment
        var_id = node.id
        assert var_id in self.var_types, f"Undefined variable {var_id}"
        self.c_src += str(var_id)
        return self.var_types[var_id]

    def visit_BinOp(self, node: ast.BinOp):
        if isinstance(node.op, ast.Pow):
            self.c_src += "powf("
            left_type = self.visit(node.left)
            self.c_src += ","
            right_type = self.visit(node.right)
            self.c_src += ")"
        else:
            raise NotImplementedError
        assert left_type in SCALAR_TYPES
        assert right_type in SCALAR_TYPES
        if left_type == "int" and right_type == "int":
            return "int"
        else:
            return "float"

    def visit_Return(self, node: ast.Return):
        self.c_src += "return "
        value_type = self.visit(node.value)
        self.c_src += ";\n"
        assert value_type in SCALAR_TYPES

    def generic_visit(self, node):
        raise NotImplementedError("Unknown node " + repr(node))


def generate_wasm_src(python_src_path) -> str:
    p_ast = get_python_ast(python_src_path)
    fun = get_functiondef(p_ast)
    fv = FunctionVisitor()
    try:
        fv.visit(fun)
    except Exception as ex:
        console.error(f"Failed: {ex}")
        console.error(f"Incomplete source: {fv.c_src}")
    return fv.c_src


# DEBUG=1 python -m webdnn.graph.custom_python_operator.generator example/custom_python_operator/square_impl.py
def main():
    generate_wasm_src(sys.argv[1])


if __name__ == "__main__":
    main()
