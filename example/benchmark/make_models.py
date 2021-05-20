import argparse
import json
import os
import subprocess
import numpy as np
import torch
import torch.onnx
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from webdnn.tensor_export import serialize_tensors

torch.manual_seed(0)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runner", "model")
RUN_OPTIMIZE = False
TARGET_MODELS = None
BACKENDS = None

def dump_expected(directory, arrays_dict):
    serialize_tensors(directory + "/expected.bin", arrays_dict)

name_all = []


def scalar(value):
    return torch.Tensor([value]).squeeze()


def rand_scalar():
    return torch.rand(1).squeeze()


def randn_scalar():
    return torch.randn(1).squeeze()

def optimize_if_requested(output_dir):
    onnx_path = f"{output_dir}/model.onnx"
    if RUN_OPTIMIZE:
        optimize_args = ["python", "-m", "webdnn.optimize_model", onnx_path, os.path.join(output_dir, "optimized")]
        if BACKENDS is not None:
            optimize_args.append("--backends")
            optimize_args.append(BACKENDS)
        subprocess.check_call(optimize_args)


def dump(name, model, input_shapes):
    name_all.append(name)
    if TARGET_MODELS is not None and name not in TARGET_MODELS:
        return
    output_dir = f"{OUTPUT_DIR}/{name}"
    os.makedirs(output_dir, exist_ok=True)
    inputs = []
    model.eval()
    for shape in input_shapes:
        if isinstance(shape, torch.Tensor):
            # 特定の入力をしたい場合はtorch.Tensor自体を与える
            inputs.append(shape)
        else:
            if len(shape) == 0:
                inputs.append(randn_scalar())  # スカラー
            else:
                inputs.append(torch.randn(*shape))
    input_names = [f"input_{i}" for i in range(len(inputs))]
    onnx_path = f"{output_dir}/model.onnx"
    with torch.no_grad():
        example_output = model(*inputs)
        if isinstance(example_output, tuple):
            output_names = [f"output_{i}" for i in range(len(example_output))]
        else:
            output_names = ["output_0"]
        torch.onnx.export(model, tuple(inputs), onnx_path,
                          verbose=True,
                          input_names=input_names,
                          output_names=output_names, opset_version=10)
    dumps = {}
    for tensor, name in zip(inputs, input_names):
        dumps[name] = tensor.numpy()
    if isinstance(example_output, tuple):
        for i, eo in enumerate(example_output):
            dumps[f"output_{i}"] = eo.numpy()
    else:
        dumps["output_0"] = example_output.numpy()
    dump_expected(output_dir, dumps)
    optimize_if_requested(output_dir)


def output_list():
    with open(f"{OUTPUT_DIR}/cases.json", "w") as f:
        json.dump(name_all, f)


def main():
    global RUN_OPTIMIZE, TARGET_MODELS, BACKENDS
    parser = argparse.ArgumentParser()
    parser.add_argument("--optimize", action="store_true", help="specify this to make optimized model (takes time)")
    parser.add_argument("--only", help="output only specific models (separated by comma)")
    parser.add_argument("--backends")
    args = parser.parse_args()
    RUN_OPTIMIZE = args.optimize
    if args.only:
        TARGET_MODELS = args.only.split(",")
    if args.backends is not None:
        BACKENDS = args.backends
    dump("resnet18", models.resnet18(pretrained=True), [(1, 3, 224, 224)])
    dump("resnet50", models.resnet50(pretrained=True), [(1, 3, 224, 224)])
    dump("conv-64-64-3-1-1", nn.Conv2d(64, 64, 3, stride=1, padding=1, bias=False), [(1, 64, 56, 56)])
    dump("conv-256-64-1-1-0", nn.Conv2d(256, 64, 1, stride=1, padding=0, bias=False), [(1, 256, 56, 56)])
    dump("conv-128-128-3-1-1", nn.Conv2d(128, 128, 3, stride=1, padding=1, bias=False), [(1, 128, 28, 28)])
    dump("conv-512-128-1-1-0", nn.Conv2d(512, 128, 1, stride=1, padding=0, bias=False), [(1, 512, 28, 28)])
    dump("conv-256-256-3-1-1", nn.Conv2d(256, 256, 3, stride=1, padding=1, bias=False), [(1, 256, 14, 14)])
    dump("conv-1024-256-1-1-0", nn.Conv2d(1024, 256, 1, stride=1, padding=0, bias=False), [(1, 1024, 14, 14)])
    output_list()


if __name__ == '__main__':
    main()
