from webdnn.backend.webgl.optimize_rules.split_texture.check_texture_size import CheckTextureSize
from webdnn.backend.webgl.optimize_rules.split_texture.split_input_texture import SplitInputTexture
from webdnn.backend.webgl.optimize_rules.split_texture.split_output_texture import SplitOutputTexture

from webdnn.backend.webgl.optimize_rules.split_texture.split_variable import SplitVariable
from webdnn.graph.optimize_rule import OptimizeRuleGroup
from webdnn.util import flags


class SplitTexture(OptimizeRuleGroup):
    """
    Split too large texture which is not supported by device.

    Procedure:

        - Find all variables whose texture size is larger than the threshold
            - threshold is given by :code:`webdnn.util.config.WEBGL_MAX_TEXTURE_SIZE`.
            - If no variable is found, this optimization is not needed. Finish.

        - For each found variable, :code:`v`,
            - attach :code:`SplitTarget` attribute to :code:`v`.

        - If any variable in graph input has `SplitTarget` attribute,
            - raise NotImplementedError (= This texture cannot be supported under current max texture size configuration)

        - If any variable in graph output has `SplitTarget` attribute,
            - raise NotImplementedError (= This texture cannot be supported under current max texture size configuration)

        - Considering sub graph which has some operators connected with split target variable :code:`v`,

                       +-{op2}-
            -{op1}- v -+
                       +-{op3}-

            There, :code:`op1` has :code:`SplitOutput` attribute and :code:`op2` and :code:`op3` have :code:`SplitInput` attribute

            - For each operator connected with :code:`v`, list up all axes which operator can split.

                ex) v's order is :code:`Order([A1, A2, A3])`.
                    op1 can split :code:`A1` and :code:`A2`.
                    op2 can split :code:`A2` and :code:`A3`.
                    op3 can split only :code:`A2`.

                In this case, `A2` can be split.

                - If no axis can be split, raise :code:`NotImplementedError`

            - Split axis `A2` in `v`,

                before)
                             +-{op2}- y1
                x -{op1}- v -+
                             +-{op3}- y2

                after)                           +-{op2'}---+
                                                 |          +--{concat}- y1
                           +- x1 -{op1_1}- v1_1 -+          |
                           |                     +-{op3'}-+ |
                 x-{split}-+                              | |
                           |                     +-{op2'}---+
                           +- x2 -{op1_2}- v1_2 -+        |
                                                 |        +----{concat}- y2
                                                 +-{op3'}-+
    """

    def flags(self):
        return [flags.optimize.WEBGL_OPTIMIZE_TEXTURE_SIZE]

    def __init__(self):
        super(SplitTexture, self).__init__([
            CheckTextureSize(),
            SplitInputTexture(),
            SplitOutputTexture(),
            SplitVariable(),
            # DumpGraph(f"cg_split_{{count}}.dot")
        ])
