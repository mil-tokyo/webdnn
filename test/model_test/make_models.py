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

class ReLU(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return F.relu(x)


class ReLUExp(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return torch.exp(F.relu(x))


class Transpose(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return torch.transpose(x, 0, 1)


class MatMul(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(128, 64, bias=False)

    def forward(self, x):
        return self.fc(x)


class MatMul2(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x, y):
        return torch.matmul(x, y)


class Gemm(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(128, 64, bias=True)

    def forward(self, x):
        return self.fc(x)


class Conv(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 64, 7, 2, 3, bias=False)

    def forward(self, x):
        return self.conv(x)


class BN(nn.Module):
    def __init__(self):
        super().__init__()
        self.bn = nn.BatchNorm2d(3)

    def forward(self, x):
        return self.bn(x)


class MaxPool(nn.Module):
    def __init__(self):
        super().__init__()
        self.pool = nn.MaxPool2d(
            kernel_size=3, stride=2, padding=0, ceil_mode=True)

    def forward(self, x):
        return self.pool(x)


class AveragePool(nn.Module):
    def __init__(self):
        super().__init__()
        # count_include_pad=True にすると、pytorch->onnxでは単独のPadオペレータが生成される
        self.pool = nn.AvgPool2d(
            kernel_size=3, stride=1, padding=0, ceil_mode=True, count_include_pad=False)

    def forward(self, x):
        return self.pool(x)


class Concat3(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, c0, c1, c2):
        return torch.cat([c0, c1, c2], dim=1)


class Concat4(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, c0, c1, c2, c3):
        return torch.cat([c0, c1, c2, c3], dim=1)


class Reshape(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        # Flattenが使われてしまいReshapeのテストとしては使えない
        return x.view(1, -1)


class Add(nn.Module):
    def forward(self, x, y):
        return x + y


class Sub(nn.Module):
    def forward(self, x, y):
        return x - y


class Mul(nn.Module):
    def forward(self, x, y):
        return x * y


class Div(nn.Module):
    def forward(self, x, y):
        return x / y


class Pow(nn.Module):
    def forward(self, x, y):
        return torch.pow(x, y)


class ResNetPartial(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        resnet = models.resnet18(pretrained=True)
        self.conv1 = resnet.conv1
        self.bn1 = resnet.bn1

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        return x


class Flatten2(nn.Module):
    def forward(self, x):
        # [a,b,c,d] -> [a,b,c*d]
        return x.flatten(2)


class Slice2d(nn.Module):
    def forward(self, x):
        return x[10:, :]


class Slice2d2(nn.Module):
    def forward(self, x):
        return x[10::4, -100:-5:3]


class Permute(nn.Module):
    def forward(self, x):
        return x.permute(2, 0, 1)


class Unsqueeze(nn.Module):
    def forward(self, x):
        return x.unsqueeze(2).unsqueeze(-1)


class Cast(nn.Module):
    def forward(self, x):
        return x.type(torch.int32)


class Sqrt(nn.Module):
    def forward(self, x):
        return torch.sqrt(x)


class Sigmoid(nn.Module):
    def forward(self, x):
        return torch.sigmoid(x)


class Tanh(nn.Module):
    def forward(self, x):
        return torch.tanh(x)


class Ceil(nn.Module):
    def forward(self, x):
        return torch.ceil(x)


class Floor(nn.Module):
    def forward(self, x):
        return torch.floor(x)


class Gather0D(nn.Module):
    def forward(self, x):
        # 1D -> scalar
        return x[3]


class Gather1D(nn.Module):
    def forward(self, x):
        return x[[2, 4, 5]]


class ReduceMean(nn.Module):
    def forward(self, x):
        return torch.mean(x, -1, keepdim=True)


class Split(nn.Module):
    def __init__(self, split_size_or_sections, dim) -> None:
        super().__init__()
        self.split_size_or_sections = split_size_or_sections
        self.dim = dim

    def forward(self, x):
        return torch.split(x, self.split_size_or_sections, dim=self.dim)


def dump_expected(directory, arrays_dict):
    serialize_tensors(directory + "/expected.bin", arrays_dict)

name_all = []


def scalar(value):
    return torch.Tensor([value]).squeeze()


def rand_scalar():
    return torch.rand(1).squeeze()


def randn_scalar():
    return torch.randn(1).squeeze()

def dump(name, model, input_shapes):
    name_all.append(name)
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
    if RUN_OPTIMIZE:
        subprocess.check_call(["python", "-m", "webdnn.optimize_model", onnx_path, os.path.join(output_dir, "optimized")])


def output_list():
    with open(f"{OUTPUT_DIR}/cases.json", "w") as f:
        json.dump(name_all, f)


def main():
    global RUN_OPTIMIZE
    parser = argparse.ArgumentParser()
    parser.add_argument("--optimize", action="store_true", help="specify this to make optimized model (takes time)")
    args = parser.parse_args()
    RUN_OPTIMIZE = args.optimize
    dump("relu", ReLU(), [(3, 4)])
    dump("relu2", ReLU(), [(100, 20, 30, 400)])
    dump("reluexp", ReLUExp(), [(3, 4)])
    dump("sqrt", Sqrt(), [torch.rand(3, 4)])
    dump("sqrtscalar", Sqrt(), [rand_scalar()])
    dump("sigmoid", Sigmoid(), [(3, 4)])
    dump("ceil", Ceil(), [(3, 4)])
    dump("floor", Floor(), [(3, 4)])
    dump("gemm", Gemm(), [(3, 128)])
    dump("matmul", MatMul(), [(3, 128)])
    dump("matmul2", MatMul2(), [(1, 3, 128), (4, 128, 1)])
    # (in_channels, out_channels, kernel_size, stride=1, padding=0, dilation=1, groups=1, bias=True, padding_mode='zeros')
    #dump("conv1", nn.Conv2d(1, 1, 1, 1, 0, bias=False), [(1, 1, 3, 3)])
    dump("conv1", nn.Conv2d(2, 4, 3, 1, 0, bias=False), [(1, 2, 8, 8)])
    dump("conv2", nn.Conv2d(3, 4, 7, 2, 3, bias=False), [(2, 3, 8, 16)])
    dump("conv3", nn.Conv2d(4, 8, 7, 2, 3,
         groups=2, bias=False), [(3, 4, 8, 16)])
    dump("conv4", nn.Conv2d(4, 8, 3, 2, 3, dilation=2,
         groups=2, bias=False), [(3, 4, 8, 16)])
    dump("conv5", nn.Conv2d(4, 8, 3, 2, 3,
         dilation=2, groups=2), [(3, 4, 8, 16)])
    dump("maxpool1", nn.MaxPool2d(kernel_size=3,
         stride=2, padding=0), [(2, 3, 10, 12)])
    dump("maxpool2", nn.MaxPool2d(kernel_size=3, stride=2,
         padding=0, ceil_mode=True), [(2, 3, 10, 12)])
    # count_include_pad=Trueのとき、Padオペレータが出力される
    #dump("avgpool1", nn.AvgPool2d(kernel_size=3, stride=2, padding=0), [(2, 3, 10, 12)])
    #dump("avgpool2", nn.AvgPool2d(kernel_size=3, stride=2, padding=0, ceil_mode=True), [(2, 3, 10, 12)])
    dump("avgpool3", nn.AvgPool2d(kernel_size=3, stride=2, padding=0,
         ceil_mode=True, count_include_pad=False), [(2, 3, 10, 12)])
    dump("globalavgpool", nn.AdaptiveAvgPool2d((1, 1)), [(2, 3, 10, 12)])
    # (2, 3, 10, 12) -< (2, 3*10*12)
    dump("flatten", nn.Flatten(), [(2, 3, 10, 12)])
    dump("add1", Add(), [(2, 3, 10, 12), (2, 3, 10, 12)])
    dump("add2", Add(), [(2, 3, 10, 12), tuple()])
    dump("add3", Add(), [(2, 3, 10, 12), (1, 3, 1, 12)])
    dump("add4", Add(), [tuple(), tuple()])
    dump("sub1", Sub(), [(2, 3, 10, 12), (2, 3, 10, 12)])
    dump("sub2", Sub(), [(2, 3, 10, 12), tuple()])
    dump("sub3", Sub(), [(2, 3, 10, 12), (1, 3, 1, 12)])
    dump("sub4", Sub(), [tuple(), tuple()])
    dump("mul1", Mul(), [(2, 3, 10, 12), (2, 3, 10, 12)])
    dump("mul2", Mul(), [(2, 3, 10, 12), tuple()])
    dump("mul3", Mul(), [(2, 3, 10, 12), (1, 3, 1, 12)])
    dump("mul4", Mul(), [tuple(), tuple()])
    dump("div1", Div(), [(2, 3, 10, 12), (2, 3, 10, 12)])
    dump("div2", Div(), [(2, 3, 10, 12), tuple()])
    dump("div3", Div(), [(2, 3, 10, 12), (1, 3, 1, 12)])
    dump("div4", Div(), [tuple(), tuple()])
    dump("pow1", Pow(), [torch.rand(2, 3, 10, 12), torch.rand(2, 3, 10, 12)])
    dump("pow2", Pow(), [torch.rand(2, 3, 10, 12), rand_scalar()])
    dump("pow3", Pow(), [torch.rand(2, 3, 10, 12), torch.rand(1, 3, 1, 12)])
    dump("pow4", Pow(), [rand_scalar(), rand_scalar()])
    dump("pow5", Pow(), [torch.rand(2, 3, 10, 12), scalar(2.0)])
    # dump("maxpool3", nn.MaxPool2d(kernel_size=3, stride=2, padding=1, dilation=2), [(2, 3, 10, 12)])
    # dump("resnet18", models.resnet18(pretrained=True), [(1, 3, 224, 224)])
    # dump("resnet18-conv0", nn.Conv2d(3, 64, 7, 2, 3), [(1, 3, 224, 224)])
    # dump("resnet18-maxpool", nn.MaxPool2d(kernel_size=3, stride=2, padding=1), [(1, 64, 64, 64)])
    # dump("resnet18-conv1", nn.Conv2d(128, 256, 3, 2, 1), [(1, 128, 32, 32)])
    # dump("resnet18-partial", ResNetPartial(), [(1, 3, 224, 224)])
    # dump("resnet50", models.resnet50(pretrained=True), [(1, 3, 224, 224)])
    dump("flatten2", Flatten2(), [(2, 3, 4, 5)])
    # dump("slice2d", Slice2d(), [(100, 200)])
    # dump("slice2d2", Slice2d2(), [(100, 200)])
    # dump("concat3", Concat3(), [(2, 3, 224, 224), (2, 8, 224, 224), (2, 1, 224, 224)])
    # dump("concat4", Concat4(), [(2, 3, 224, 224), (2, 8, 224, 224), (2, 1, 224, 224), (2, 9, 224, 224)])
    dump("transpose", Permute(), [(3, 4, 5)])
    dump("unsqueeze", Unsqueeze(), [(3, 4, 5, 6)])
    dump("cast", Cast(), [(3, 4)])
    # dump("gather0d", Gather0D(), [(10,)])
    # #dump("gather1d", Gather1D(), [(10,)])
    dump("reducemean", ReduceMean(), [(3, 4, 5, 6)])
    dump("softmax", torch.nn.Softmax(dim=-1), [(3, 4, 5, 6)])
    dump("split1", Split([2, 3, 5, 7, 60-2-3-5-7], -1), [(3, 4, 5, 60)])
    dump("split2", Split([2, 3, 5, 7, 40-2-3-5-7], 1), [(3, 40, 5, 6)])
    dump("split3", Split(4, 0), [(30, 4, 5, 6)])
    output_list()


if __name__ == '__main__':
    main()
