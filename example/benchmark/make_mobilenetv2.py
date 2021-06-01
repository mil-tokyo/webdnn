import argparse
import json
import os
import shutil
import subprocess
import sys
import numpy as np
import torch
import torch.onnx
import torch.nn as nn
import torch.nn.functional as F
from webdnn.tensor_export import serialize_tensors
# do not import torchvision


sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))

torch.manual_seed(0)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runner", "external_model")

def dump_expected(directory, arrays_dict):
    serialize_tensors(directory + "/expected.bin", arrays_dict)

def scalar(value):
    return torch.Tensor([value]).squeeze()


def rand_scalar():
    return torch.rand(1).squeeze()


def randn_scalar():
    return torch.randn(1).squeeze()

def dump(name, model, input_shapes):
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

def make_input_data():
    from torchvision import transforms
    from PIL import Image
    import skimage

    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(Image.fromarray(skimage.data.coffee()))
    input_batch = input_tensor.unsqueeze(0)
    return input_batch

def main():
    # torch.hub.load imports special torchvision from temporary directory.
    # It is impossible to load other model which uses standard torchvision in the same process.
    model = torch.hub.load('pytorch/vision:v0.9.0', 'mobilenet_v2', pretrained=True)
    preprocessed_image = make_input_data()
    dump("mobilenet_v2", model, [preprocessed_image])

if __name__ == '__main__':
    main()
