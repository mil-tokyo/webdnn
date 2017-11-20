from typing import List

from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import texture_stride, texture_shape, convert_coord
from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA


@WebGLDescriptorGenerator.register_handler(ConvertRtoRGBA)
def convert_r_to_rgba(op: ConvertRtoRGBA) -> List[Kernel]:
    x = op.inputs["x0"]
    y = op.outputs["y"]

    assert ChannelMode.get(x) == ChannelModeEnum.R
    assert ChannelMode.get(y) == ChannelModeEnum.RGBA
    assert x.order == y.order

    shape_x = texture_shape(x)
    stride_x = texture_stride(x)
    shape_y = texture_shape(y)
    stride_y = texture_stride(y)

    code = KernelCode(["""
void main() {
    float y0 = texture2D(""", x, ", ", convert_coord("ivec3(gl_FragCoord.y, gl_FragCoord.x, 0)", shape_y, stride_y, shape_x, stride_x), """.yx).r;
    float y1 = texture2D(""", x, ", ", convert_coord("ivec3(gl_FragCoord.y, gl_FragCoord.x, 1)", shape_y, stride_y, shape_x, stride_x), """.yx).r;
    float y2 = texture2D(""", x, ", ", convert_coord("ivec3(gl_FragCoord.y, gl_FragCoord.x, 2)", shape_y, stride_y, shape_x, stride_x), """.yx).r;
    float y3 = texture2D(""", x, ", ", convert_coord("ivec3(gl_FragCoord.y, gl_FragCoord.x, 3)", shape_y, stride_y, shape_x, stride_x), """.yx).r;

    gl_FragColor = vec4(y0, y1, y2, y3);
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
