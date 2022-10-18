import argparse
import json
import os
from os.path import abspath
import subprocess
import onnx
from webdnn.passes import run_passes
from webdnn.tensor_export import export_initializers

ALL_BACKENDS = ["webgl2-16384", "webgl2-4096", "webgl1-16384", "webgl1-4096", "wasm", "cpu"] # "webgpu" is not yet supported
SUBPROCESS_SHELL = os.name=='nt'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("onnx_model")
    parser.add_argument("dst_dir")
    parser.add_argument("--compression", type=int, default=0, help="compression algorithm number (0=no compression)")
    parser.add_argument("--backends", default=",".join(ALL_BACKENDS))
    args = parser.parse_args()
    backends = args.backends.split(",")
    os.makedirs(args.dst_dir, exist_ok=True)
    for backend in backends:
        src_model = onnx.load_model(args.onnx_model)
        optimization_result = run_passes(src_model, backend)
        # print(optimization_result)
        optimization_result.write_code(ROOT_DIR)
        optimized_model = src_model
        tensor_pathes = export_initializers(os.path.join(args.dst_dir, f"weight-{backend}-{{}}.bin"), optimized_model, optimization_result.initializers, 4 * 1024 * 1024, args.compression)
        weight_paths = ":".join([os.path.basename(tensor_path) for tensor_path in tensor_pathes])
        optimized_model.metadata_props.append(onnx.StringStringEntryProto(key="WebDNN2.WeightPaths", value=weight_paths))
        optimized_model.metadata_props.append(onnx.StringStringEntryProto(key="WebDNN2.TensorMoveOptions", value=json.dumps(optimization_result.tensor_move_options)))
        onnx.save_model(optimized_model, os.path.join(args.dst_dir, f"model-{backend}.onnx"))
        if backend == "wasm":
            subprocess.check_call(["yarn", "shader:wasm"], shell=SUBPROCESS_SHELL, cwd=ROOT_DIR)
        if backend == "webgpu":
            subprocess.check_call(["yarn", "shader:webgpu"], shell=SUBPROCESS_SHELL, cwd=ROOT_DIR)
        subprocess.check_call(["yarn", "makeShaderList"], shell=SUBPROCESS_SHELL, cwd=ROOT_DIR)
        subprocess.check_call(["yarn", f"build:{backend}", "-o", os.path.abspath(args.dst_dir)], shell=SUBPROCESS_SHELL, cwd=ROOT_DIR)
        optimization_result.remove_code(ROOT_DIR)
    # reset shader list file (remove autogen entry)
    subprocess.check_call(["yarn", "makeShaderList"], shell=SUBPROCESS_SHELL, cwd=ROOT_DIR)


if __name__ == "__main__":
    main()
