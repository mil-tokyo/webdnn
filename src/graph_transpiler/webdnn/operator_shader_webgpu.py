from webdnn.operator_shader import OperatorShader

class OperatorShaderWebGPU(OperatorShader):
    ts_code: str
    shader_name: str
    glsl_code: str

    def __init__(self, ts_code: str, shader_name: str, glsl_code: str) -> None:
        super().__init__()
        self.ts_code = ts_code
        self.glsl_code = glsl_code
        self.shader_name = shader_name
