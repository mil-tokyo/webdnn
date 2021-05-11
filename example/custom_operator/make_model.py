import os
import torch
from torch.autograd import Function
import torch.nn.functional as F
import numpy as np

class TwiceFunction(Function):
    @staticmethod
    def symbolic(g, x):
        y = g.op("foo_domain::Twice", x)
        return y

    @staticmethod
    def forward(ctx, input):
        numpy_input = input.detach().numpy()
        result = numpy_input * 2
        return input.new(result)
    
    @staticmethod
    def backward(ctx, grad_output):
        numpy_go = grad_output.numpy()
        result = numpy_go * 2
        return grad_output.new(result)

def twice(input):
    return TwiceFunction.apply(input)

class MyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
    
    def forward(self, x):
        h = twice(x)
        h = F.relu(h)
        return h

def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    model = MyModel()
    example_input = torch.zeros((2, 3))
    # ONNX model contains two operators: Twice (custom), Relu (standard)
    torch.onnx.export(model, (example_input, ), os.path.join(output_dir, "model.onnx"))
    # TODO: how to avoid TracerWarning?

if __name__ == '__main__':
    main()
