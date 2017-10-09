from typing import List

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelMode, ChannelModeEnum
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape, simplify_orders
from webdnn.backend.webgl.operators.convert_r_to_rgba import ConvertRtoRGBA
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.axis import AxisKeyDict
from webdnn.util.misc import mul

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, sampler_x)%%;

%%UNIFORM(vec2, texture_stride_y)%%;
%%UNIFORM(vec4, variable_shape_y)%%;
%%UNIFORM(vec4, variable_stride_y)%%;

%%UNIFORM(vec2, texture_shape_x)%%;
%%UNIFORM(vec2, texture_stride_x)%%;
%%UNIFORM(vec4, variable_shape_x)%%;
%%UNIFORM(vec4, variable_stride_x)%%;

void main() {
    vec4 variable_position_0  = convert_position(gl_FragCoord.xy, texture_stride_y, variable_stride_y, variable_shape_y, 0);
    vec4 variable_position_1  = convert_position(gl_FragCoord.xy, texture_stride_y, variable_stride_y, variable_shape_y, 1);
    vec4 variable_position_2  = convert_position(gl_FragCoord.xy, texture_stride_y, variable_stride_y, variable_shape_y, 2);
    vec4 variable_position_3  = convert_position(gl_FragCoord.xy, texture_stride_y, variable_stride_y, variable_shape_y, 3);
    
    float y0 = texture2D(sampler_x, convert_coord(variable_position_0, variable_stride_x, texture_stride_x, texture_shape_x)).r;
    float y1 = texture2D(sampler_x, convert_coord(variable_position_1, variable_stride_x, texture_stride_x, texture_shape_x)).r;
    float y2 = texture2D(sampler_x, convert_coord(variable_position_2, variable_stride_x, texture_stride_x, texture_shape_x)).r;
    float y3 = texture2D(sampler_x, convert_coord(variable_position_3, variable_stride_x, texture_stride_x, texture_shape_x)).r;

    gl_FragColor = vec4(y0, y1, y2, y3);
}
"""


@WebGLDescriptorGenerator.register_handler(ConvertRtoRGBA)
def convert_r_to_rgba(op: ConvertRtoRGBA) -> List[Kernel]:
    x = op.inputs["x0"]
    y = op.outputs["y"]

    assert ChannelMode.get(x) == ChannelModeEnum.R
    assert ChannelMode.get(y) == ChannelModeEnum.RGBA

    orders, shape_dicts = simplify_orders([x, y])
    shapes = {v: [shape_dicts[v][a] for a in orders[v].axes] for v in [x, y]}
    strides = {v: [mul(shapes[v][orders[v].axes_dict[a] + 1:]) for a in orders[v].axes] for v in [x, y]}
    stride_dicts = {v: AxisKeyDict(orders[v].axes, strides[v]) for v in [x, y]}

    # Change x's shapes and strides order to same as y's order
    shapes[x] = [shape_dicts[x][a] if a in orders[x].axes else 1 for a in orders[y].axes]
    strides[x] = [stride_dicts[x][a] if a in orders[x].axes else 1 for a in orders[y].axes]

    # Padding shapes and strides to 4D
    if orders[y].ndim > 4:
        raise NotImplementedError(f"Too large number of dimension: {y}")

    for v in [x, y]:
        shape = shapes[v]
        stride = strides[v]
        while len(shape) < 4:
            stride.append(1)
            shape.append(1)

    name_injector = KernelNameInjector(op)
    uniform_injector = UniformInjector()
    uniform_injector.register({
        "sampler_x": x,

        "texture_stride_y": texture_stride(y),
        "variable_shape_y": shapes[y],
        "variable_stride_y": strides[y],

        "texture_shape_x": texture_shape(x),
        "texture_stride_x": texture_stride(x),
        "variable_shape_x": shapes[x],
        "variable_stride_x": strides[x],
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

    return [kernel]
