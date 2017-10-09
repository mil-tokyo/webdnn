from typing import List, Sequence

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.split_axis import SplitAxis

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, sampler_x)%%;

%%UNIFORM(vec2, texture_stride_y)%%;
%%UNIFORM(vec4, variable_shape_y)%%;
%%UNIFORM(vec4, variable_stride_y)%%;

%%UNIFORM(vec4, variable_shape_x)%%;
%%UNIFORM(vec4, variable_stride_x)%%;
%%UNIFORM(vec2, texture_stride_x)%%;
%%UNIFORM(vec2, texture_shape_x)%%;

%%UNIFORM(vec4, offset)%%;

void main() {
    vec4 variable_position_y = convert_position(gl_FragCoord.xy, texture_stride_y, variable_stride_y, variable_shape_y);    
    vec4 variable_position_x = variable_position_y + offset;
    float x = texture2D(sampler_x, convert_coord(variable_position_x, variable_stride_x, texture_stride_x, texture_shape_x)).r;

    gl_FragColor = vec4(x, 0, 0, 0);
}
"""


def _pad_to_4d(arr: Sequence[int], val: int = 1):
    assert len(arr) <= 4, ValueError

    arr = list(arr)
    while len(arr) < 4:
        arr.append(val)

    return arr


@WebGLDescriptorGenerator.register_handler(SplitAxis)
def split_axis(op: SplitAxis) -> List[Kernel]:
    x = op.inputs["x"]
    ys = [op.outputs[f"y{i}"] for i in range(len(op.outputs))]
    sections = [0] + op.sections
    axis = op.axis

    kernels = []

    for i, y in enumerate(ys):
        assert x.order.check_same_axes(y.order)
        assert ChannelMode.get(x) == ChannelMode.get(y) == ChannelModeEnum.R

        name_injector = KernelNameInjector(op)
        uniform_injector = UniformInjector()

        offset = [sections[i] if a == axis else 0 for a in y.order.axes]
        uniform_injector.register({
            "sampler_x": x,

            "texture_stride_y": texture_stride(y),
            "variable_shape_y": _pad_to_4d(y.shape),
            "variable_stride_y": _pad_to_4d(y.stride),

            "texture_shape_x": texture_shape(x),
            "texture_stride_x": texture_stride(x),
            "variable_shape_x": _pad_to_4d([x.shape_dict[a] for a in y.order.axes]),
            "variable_stride_x": _pad_to_4d([x.stride_dict[a] for a in y.order.axes]),

            "offset": _pad_to_4d(offset, 0)
        })

        source = template
        source = uniform_injector.inject(source)
        source = name_injector.inject(source)
        kernel = Kernel(
            source,
            name_injector.name,
            uniform_injector.samplers,
            uniform_injector.uniforms,
            y
        )
        kernels.append(kernel)

    return kernels
