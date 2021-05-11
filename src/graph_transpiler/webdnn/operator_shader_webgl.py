from webdnn.operator_shader import OperatorShader

class OperatorShaderWebGL(OperatorShader):
    ts_code: str

    def __init__(self, ts_code: str) -> None:
        super().__init__()
        self.ts_code = ts_code
