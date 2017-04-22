from graph_builder.backend.webgpu.optimizers.webgpu_conv_optimizer import WebGPUConvOptimizer
from graph_builder.optimizer.optimizer import Optimizer


class WebGPUOptimizer(Optimizer):
    def __init__(self):
        super(WebGPUOptimizer, self).__init__()

        self.register(WebGPUConvOptimizer())
