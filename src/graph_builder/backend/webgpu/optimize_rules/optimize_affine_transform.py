from graph_builder.backend.webgpu.optimize_rules.sub_rules.combine_affine_transform import CombineAffineTransform
from graph_builder.backend.webgpu.optimize_rules.sub_rules.upgrade_constant_bias_to_affine_transform import \
    UpgradeConstantBiasToAffineTransform
from graph_builder.backend.webgpu.optimize_rules.sub_rules.upgrade_constant_scale_to_affine_transform import \
    UpgradeConstantScaleToAffineTransform
from graph_builder.optimize_rule.optimize_rule import OptimizeRule


class OptimizeAffineTransform(OptimizeRule):
    def __init__(self):
        super(OptimizeAffineTransform, self).__init__()

        self.register(UpgradeConstantBiasToAffineTransform())
        self.register(UpgradeConstantScaleToAffineTransform())
        self.register(CombineAffineTransform())
