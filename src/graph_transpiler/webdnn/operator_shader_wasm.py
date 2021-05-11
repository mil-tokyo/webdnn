from webdnn.operator_shader import OperatorShader

class OperatorShaderWasm(OperatorShader):
    ts_code: str
    shader_name: str
    cpp_code: str

    def __init__(self, ts_code: str, shader_name: str, cpp_code: str) -> None:
        super().__init__()
        self.ts_code = ts_code
        self.shader_name = shader_name
        self.cpp_code = cpp_code
