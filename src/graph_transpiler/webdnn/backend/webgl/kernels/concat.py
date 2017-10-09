from typing import List, Sequence

from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgl.attributes.channel_mode import ChannelMode
from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernels.util import FragmentShaderPreamble, texture_stride, texture_shape
from webdnn.backend.webgl.uniform_injector import UniformInjector
from webdnn.graph.operators.concat import Concat

template = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, sampler_x)%%;
%%UNIFORM(sampler2D, sampler_workspace)%%;

%%UNIFORM(vec2, texture_shape_workspace)%%;

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
    vec4 variable_position_x = variable_position_y - offset;

    gl_FragColor = (any(lessThan(variable_position_x, vec4(0.0, 0.0, 0.0, 0.0))) || any(greaterThanEqual(variable_position_x, variable_shape_x))) ? 
        texture2D(sampler_workspace, gl_FragCoord.xy / texture_shape_workspace) :
        texture2D(sampler_x, convert_coord(variable_position_x, variable_stride_x, texture_stride_x, texture_shape_x));
}
"""

template2 = FragmentShaderPreamble + """
%%UNIFORM(sampler2D, sampler_y)%%;
%%UNIFORM(vec2, texture_shape_y)%%;

void main() {
    gl_FragColor = texture2D(sampler_y, gl_FragCoord.xy / texture_shape_y);
}
"""


def _pad_to_4d(arr: Sequence[int], val: int = 1):
    assert len(arr) <= 4, ValueError

    arr = list(arr)
    while len(arr) < 4:
        arr.append(val)

    return arr


@WebGLDescriptorGenerator.register_handler(Concat)
def concat(op: Concat) -> List[Kernel]:
    xs = [op.inputs[f"x{i}"] for i in range(len(op.inputs) - 1)]
    workspace = op.inputs["workspace"]
    y = op.outputs["y"]
    axis = op.axis

    kernels = []
    sections = [0]

    for x in xs[1:]:
        sections.append(sections[-1] + x.shape_dict[axis])

    for i, x in enumerate(xs):
        assert x.order.check_same_axes(y.order)
        assert ChannelMode.get(x) == ChannelMode.get(y)

        offset = [sections[i] if a == axis else 0 for a in y.order.axes]

        name_injector = KernelNameInjector(op)
        uniform_injector = UniformInjector()
        uniform_injector.register({
            "sampler_x": x,
            "sampler_workspace": workspace,

            "texture_shape_workspace": texture_shape(workspace),

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

        name_injector2 = KernelNameInjector(op)
        uniform_injector2 = UniformInjector()
        uniform_injector2.register({
            "sampler_y": y,
            "texture_shape_y": texture_shape(y),
        })
        source2 = template2
        source2 = uniform_injector2.inject(source2)
        source2 = name_injector2.inject(source2)
        kernel2 = Kernel(
            source2,
            name_injector2.name,
            uniform_injector2.samplers,
            uniform_injector2.uniforms,
            workspace
        )
        kernels.append(kernel2)

    return kernels
