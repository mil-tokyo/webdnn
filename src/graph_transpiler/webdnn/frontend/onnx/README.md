# ONNX frontend

WebDNN Converter Frontend for [Open Neural Network Exchange (ONNX) format](http://onnx.ai/).

## Setup

### ONNX

If you use anaconda, it completes by just one command.

```bash
conda install -c conda-forge onnx
```

In other case, see [onnx's github repository(https://github.com/onnx/onnx)](https://github.com/onnx/onnx).

You can verify it was installed correctly with the following command.

```bash
python -c "import onnx"
```

### PyTorch

PyTorch supports onnx. Its model first converted to onnx, then converted with ONNX frontend.

## Example

```python
"""
This code is based on http://pytorch.org/docs/master/onnx.html
"""
from torch.autograd import Variable
import torch.onnx
import torchvision
import onnx
from webdnn.frontend.onnx import ONNXConverter

# export PyTorch's AlexNet model
dummy_input = Variable(torch.randn(1, 3, 224, 224))
model = torchvision.models.alexnet(pretrained=True)
torch.onnx.export(model, dummy_input, "alexnet.proto", verbose=True)

# import model in onnx
model = onnx.load("alexnet.proto")

# convert
graph = ONNXConverter().convert(model)
```
