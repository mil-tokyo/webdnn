import os
import torch
import torch.nn.functional as F
import numpy as np

class MyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
    
    def forward(self, x):
        h = F.relu(x)
        return h

def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
    os.makedirs(output_dir, exist_ok=True)

    model = MyModel()
    example_input = torch.zeros((2, 3))
    torch.onnx.export(model, (example_input, ), os.path.join(output_dir, "model.onnx"))

if __name__ == '__main__':
    main()
