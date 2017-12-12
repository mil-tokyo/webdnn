from typing import List

import numpy as np

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import convert_position, texture_stride, texture_shape, vec2
from webdnn.backend.webgl.operators.convert_rgba_to_r import ConvertRGBAtoR


@WebGLDescriptorGenerator.register_handler(ConvertRGBAtoR)
def convert_rgba_to_r(op: ConvertRGBAtoR) -> List[Kernel]:
    x = op.inputs["x0"]
    y = op.outputs["y"]

    assert ChannelMode.get(x) == ChannelModeEnum.RGBA
    assert ChannelMode.get(y) == ChannelModeEnum.R
    assert x.order == y.order

    # noinspection PyUnresolvedReferences
    inv_x_shape = [np.double(1) / np.double(v) for v in texture_shape(x)[:2][::-1]]

    code = KernelCode(["""
void main() {
    ivec3 texture_position_x = """, convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], texture_shape(x),
                                                     texture_stride(x)), """;
    vec2 texture_coord_x = (vec2(texture_position_x.yx) + 0.5) * """, vec2(inv_x_shape), """;
    vec4 x = texture2D(""", x, """, texture_coord_x);

    gl_FragColor.r = texture_position_x.z == 0 ? x.r :
                     texture_position_x.z == 1 ? x.g :
                     texture_position_x.z == 2 ? x.b :
                     x.a;
}
"""], name=op.__class__.__name__)
    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )]
