import argparse
import os
from os.path import abspath
import subprocess
import onnx
from webdnn.passes import run_passes
from webdnn.tensor_export import export_initializers

# BACKENDS = ["webgpu", "webgl", "wasm", "cpu"]
BACKENDS = ["webgl", "wasm", "cpu"]
SUBPROCESS_SHELL = os.name=='nt'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("onnx_model")
    parser.add_argument("dst_dir")
    parser.add_argument("--compression", type=int, default=0, help="compression algorithm number (0=no compression)")
    args = parser.parse_args()
    os.makedirs(args.dst_dir, exist_ok=True)
    for backend in BACKENDS:
        src_model = onnx.load_model(args.onnx_model)
        optimization_result = run_passes(src_model, backend)
        # print(optimization_result)
        optimization_result.write_code(ROOT_DIR)
        optimized_model = src_model
        tensor_pathes = export_initializers(os.path.join(args.dst_dir, f"weight-{backend}-{{}}.bin"), optimized_model, 4 * 1024 * 1024, args.compression)
        weight_paths = ":".join([os.path.basename(tensor_path) for tensor_path in tensor_pathes])
        optimized_model.metadata_props.append(onnx.StringStringEntryProto(key="WebDNN2.WeightPaths", value=weight_paths))
        onnx.save_model(optimized_model, os.path.join(args.dst_dir, f"model-{backend}.onnx"))
    subprocess.check_call(["yarn", "shader:wasm"], shell=SUBPROCESS_SHELL)
    subprocess.check_call(["yarn", "shader:webgpu"], shell=SUBPROCESS_SHELL)
    subprocess.check_call(["yarn", "makeShaderList"], shell=SUBPROCESS_SHELL)
    for backend in BACKENDS:
        subprocess.check_call(["yarn", f"build:{backend}", "-o", os.path.abspath(args.dst_dir)], shell=SUBPROCESS_SHELL)

if __name__ == "__main__":
    main()
