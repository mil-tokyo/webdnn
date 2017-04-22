from graph_builder.backend.webgpu.optimizers.opptimize_affine_transform import OptimizeAffineTransform
from graph_builder.backend.webgpu.optimizers.optimize_convolution2d import OptimizeConvolution2D
from graph_builder.backend.webgpu.optimizers.optimize_deconvolution2d import OptimizeDeconvolution2D
from graph_builder.optimizer.optimizer import Optimizer


class WebGPUOptimizer(Optimizer):
    def __init__(self):
        super(WebGPUOptimizer, self).__init__()

        self.register(OptimizeConvolution2D())
        self.register(OptimizeDeconvolution2D())
        self.register(OptimizeAffineTransform())
