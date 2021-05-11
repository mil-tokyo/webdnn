import os
import glob
from webdnn.optimization_pass import OptimizationPassResult

class OptimizationPassResultWasm(OptimizationPassResult):
    def write_code(self, root_directory: str):
        directory = os.path.join(root_directory, "src/descriptor_runner/operators/wasm/operators/autogen")
        for path in glob.glob(os.path.join(directory, "*.ts")):
            os.remove(path)
        for key, s in self.operator_shaders.items():
            with open(os.path.join(directory, f"{key}.ts"), "w") as f:
                f.write(s.ts_code)
        directory = os.path.join(root_directory, "src/shader/wasm/src/kernels/autogen")
        for path in glob.glob(os.path.join(directory, "*.cpp")):
            os.remove(path)
        for key, s in self.operator_shaders.items():
            with open(os.path.join(directory, f"{key}.cpp"), "w") as f:
                f.write(s.cpp_code)
