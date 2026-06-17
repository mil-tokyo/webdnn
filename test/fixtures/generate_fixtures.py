"""Generate small, torch-free ONNX fixtures + expected.bin for browser tests.

Run with: npm run fixtures
Outputs into test/model_test/runner/model/<case>/ and writes cases.json.
"""
import json
import os
import sys

import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "graph_transpiler"))
from webdnn.tensor_export import serialize_tensors  # noqa: E402

OUTPUT_DIR = os.path.join(REPO_ROOT, "test", "model_test", "runner", "model")


def make_single_op_model(op_type, input_names, output_name, shape, attrs=None):
    inputs = [helper.make_tensor_value_info(n, TensorProto.FLOAT, shape) for n in input_names]
    output = helper.make_tensor_value_info(output_name, TensorProto.FLOAT, shape)
    node = helper.make_node(op_type, input_names, [output_name], **(attrs or {}))
    graph = helper.make_graph([node], f"{op_type}_graph", inputs, [output])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    model.ir_version = 9
    onnx.checker.check_model(model)
    return model


def dump_case(name, model, feeds):
    case_dir = os.path.join(OUTPUT_DIR, name)
    os.makedirs(case_dir, exist_ok=True)
    onnx.save(model, os.path.join(case_dir, "model.onnx"))
    sess = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"])
    output_names = [o.name for o in sess.get_outputs()]
    outputs = sess.run(output_names, feeds)
    tensors = {}
    for n, arr in feeds.items():
        tensors[n] = np.ascontiguousarray(arr, dtype=np.float32)
    for n, arr in zip(output_names, outputs):
        tensors[n] = np.ascontiguousarray(arr, dtype=np.float32)
    serialize_tensors(os.path.join(case_dir, "expected.bin"), tensors)
    print("wrote", name)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rng = np.random.default_rng(0)
    cases = []

    x = rng.standard_normal((1, 8)).astype(np.float32)
    dump_case("relu", make_single_op_model("Relu", ["input_0"], "output_0", [1, 8]), {"input_0": x})
    cases.append({"name": "relu", "large": False})

    a = rng.standard_normal((1, 8)).astype(np.float32)
    b = rng.standard_normal((1, 8)).astype(np.float32)
    dump_case("add", make_single_op_model("Add", ["input_0", "input_1"], "output_0", [1, 8]), {"input_0": a, "input_1": b})
    cases.append({"name": "add", "large": False})

    x2 = rng.standard_normal((1, 8)).astype(np.float32)
    dump_case("sigmoid", make_single_op_model("Sigmoid", ["input_0"], "output_0", [1, 8]), {"input_0": x2})
    cases.append({"name": "sigmoid", "large": False})

    with open(os.path.join(OUTPUT_DIR, "cases.json"), "w", newline="\n") as f:
        json.dump(cases, f, indent=2)
    print("wrote cases.json with", len(cases), "cases")


if __name__ == "__main__":
    main()
