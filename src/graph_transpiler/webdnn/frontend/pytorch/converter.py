"""
PyTorch Frontend
"""
import tempfile
from os import path

from webdnn.frontend.converter import Converter
from webdnn.frontend.onnx import ONNXConverter
from webdnn.frontend.util import semver
from webdnn.graph.graph import Graph
from webdnn.util import console

FLAG_PYTORCH_INSTALLED = False
try:
    import torch
    import torch.onnx

    VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = semver(torch.__version__)
    if not ((VERSION_MAJOR == 0) and (VERSION_MINOR >= 0.3)):
        raise NotImplementedError(f"WebDNN supports PyTorch >= v0.3 Currently, PyTorch {torch.__version__} is installed.")

    FLAG_PYTORCH_INSTALLED = True

except ImportError as e:
    console.debug("PyTorch is not completely installed.")
    pass

FLAG_ONNX_INSTALLED = False
try:
    import onnx

    FLAG_ONNX_INSTALLED = True

except ImportError as e:
    console.debug("ONNX is not completely installed.")
    pass


class PyTorchConverter(Converter["torch.nn.Module"]):
    """PyTorchConverter()

    Converter for `PyTorch <http://pytorch.org/>`_.

    In conversion, model is exported as ONNX format, and then converted by :class:`~webdnn.frontend.onnx.ONNXConverter`.
    Therefore both torch and onnx python package are required.
    """

    def __init__(self):
        super(PyTorchConverter, self).__init__()

        if not FLAG_PYTORCH_INSTALLED:
            raise ImportError("""
Module "pytorch" cannot be imported. Please check that follow command works correctly.

    python -c "import torch"

""")

        if not FLAG_ONNX_INSTALLED:
            raise ImportError("""
Module "onnx" cannot be imported. Please check that follow command works correctly.

    python -c "import onnx"

""")

    def convert(self, model: "torch.nn.Module", dummy_inputs) -> Graph:
        """convert(model)

        Convert PyTorch computational graph into WebDNN IR.

        .. admonition:: example

            Convert PyTorch pre-trained AlexNet model.

            .. code::

                import torch, torchvision
                from webdnn.frontend.pytorch import PyTorchConverter

                model = torchvision.models.alexnet(pretrained=True)
                dummy_input = torch.autograd.Variable(torch.randn(1, 3, 224, 224))

                graph = PyTorchConverter().convert(model, dummy_input)

        Returns:
            (:class:`~webdnn.Graph`): WebDNN Graph
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            proto_path = path.join(tmpdir, "model.proto")
            torch.onnx.export(model, dummy_inputs, proto_path, verbose=False)
            graph = ONNXConverter().convert(onnx.load(proto_path))

        return graph
