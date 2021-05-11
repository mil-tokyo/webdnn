import argparse
import json
import os
import subprocess
import urllib.request
import numpy as np
import torch
import torch.onnx
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from webdnn.tensor_export import serialize_tensors

torch.manual_seed(0)


def export_test_case(output_dir, model):
    example_input = torch.randn((1, 3, 224, 224))
    with torch.no_grad():
        example_output = model(example_input)
    serialize_tensors(os.path.join(output_dir, "expected.bin"), {
        "input": example_input.numpy(),
        "output": example_output.numpy(),
    })

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        # resnet does not include softmax
        self.resnet = models.resnet50(pretrained=True)
    
    def forward(self, x):
        h = self.resnet(x)
        h = F.softmax(h, dim=-1)
        return h

def download_sample_image(path, url):
    if os.path.exists(path):
        return
    urllib.request.urlretrieve(url, path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--optimize", action="store_true", help="specify this to make optimized model (takes time)")
    args = parser.parse_args()
    model = Model()

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

    os.makedirs(output_dir, exist_ok=True)

    download_sample_image(os.path.join(output_dir, "000000039769.jpg"), 'http://images.cocodataset.org/val2017/000000039769.jpg')

    onnx_path = os.path.join(output_dir, "model.onnx")
    
    with torch.no_grad():
        torch.onnx.export(model, (torch.zeros((1, 3, 224, 224))), onnx_path,
                          verbose=True,
                          input_names=["input"],
                          output_names=["output"], opset_version=10)
    
    export_test_case(output_dir, model)
    if args.optimize:
        subprocess.check_call(["python", "-m", "webdnn.optimize_model", onnx_path, os.path.join(output_dir, "optimized")])

if __name__ == '__main__':
    main()
