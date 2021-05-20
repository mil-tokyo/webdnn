import os
import glob
from webdnn.optimization_pass import OptimizationPassResult

class OptimizationPassResultWebGL(OptimizationPassResult):
    def write_code(self, root_directory: str):
        self.remove_code(root_directory)
        directory = os.path.join(root_directory, "src/descriptor_runner/operators/webgl/operators/autogen")
        for key, s in self.operator_shaders.items():
            with open(os.path.join(directory, f"{key}.ts"), "w") as f:
                f.write(s.ts_code)

    def remove_code(self, root_directory: str):
        directory = os.path.join(root_directory, "src/descriptor_runner/operators/webgl/operators/autogen")
        for path in glob.glob(os.path.join(directory, "*.ts")):
            os.remove(path)
