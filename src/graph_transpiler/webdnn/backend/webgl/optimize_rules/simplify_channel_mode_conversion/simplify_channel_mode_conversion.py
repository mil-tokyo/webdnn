from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_nonsense_channel_mode_conversion import \
    SimplifyNonsenseChannelModeConversion
from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_redundant_channel_mode_conversion import \
    SimplifyRedundantChannelModeConversion
from webdnn.graph.optimize_rule import OptimizeRuleGroup


class SimplifyChannelModeConversion(OptimizeRuleGroup):
    def __init__(self):
        super(SimplifyChannelModeConversion, self).__init__([
            SimplifyRedundantChannelModeConversion(),
            SimplifyNonsenseChannelModeConversion()
        ])
