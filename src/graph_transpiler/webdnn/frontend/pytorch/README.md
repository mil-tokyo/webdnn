# PyTorch frontend

WebDNN Converter Frontend for PyTorch.

This converter convert PyTorch model through [ONNX](http://onnx.ai/) format.

PyTorch supports onnx, but currently (12.01.2017), `torch.onnx` module is not included in release build of pytorch.
You have to build torch from source. See [https://github.com/pytorch/pytorch#from-source](https://github.com/pytorch/pytorch#from-source).

## Example

```python
import torch, torchvision
from webdnn.frontend.pytorch import PyTorchConverter

model = torchvision.models.alexnet(pretrained=True)
dummy_input = torch.autograd.Variable(torch.randn(1, 3, 224, 224))

graph = PyTorchConverter().convert(model, dummy_input)
```
