from webdnn.backend.webgpu.optimize_rules.sub_rules.add_inline_inplace_attribute_webgpu import AddInlineInplaceAttribute
from webdnn.backend.webgpu.optimize_rules.sub_rules.add_post_inline_inplace_attribute_webgpu import AddPostInlineInplaceAttribute
from webdnn.backend.webgpu.optimize_rules.sub_rules.inject_inline_inplace import InjectInlineInplace
from webdnn.graph.optimize_rule import OptimizeRule


class OptimizeInlineInplace(OptimizeRule):
    def __init__(self):
        super(OptimizeInlineInplace, self).__init__()

        self.register(AddInlineInplaceAttribute())
        self.register(AddPostInlineInplaceAttribute())
        self.register(InjectInlineInplace())
