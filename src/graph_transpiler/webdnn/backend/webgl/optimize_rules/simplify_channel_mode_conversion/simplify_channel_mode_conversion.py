from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_inout_channel_mode_conversion import \
    SimplifyInOutChannelModeConversion
from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_nonsense_channel_mode_conversion import \
    SimplifyNonsenseChannelModeConversion
from webdnn.backend.webgl.optimize_rules.simplify_channel_mode_conversion.simplify_redundant_channel_mode_conversion import \
    SimplifyRedundantChannelModeConversion
from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.util import flags


class SimplifyChannelModeConversion(OptimizeRuleGroup):
    def __init__(self):
        super(SimplifyChannelModeConversion, self).__init__([
            SimplifyRedundantChannelModeConversion(),
            SimplifyNonsenseChannelModeConversion(),
            SimplifyInOutChannelModeConversion()
        ])

    def flags(self):
        return [
            flags.optimize.OPTIMIZE,
            flags.optimize.SIMPLIFY_CHANNEL_MODE_CONVERSION
        ]
