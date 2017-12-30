from typing import List

from webdnn.backend.webgl.generator import WebGLDescriptorGenerator
from webdnn.backend.webgl.kernel import Kernel
from webdnn.backend.webgl.kernel_code import KernelCode
from webdnn.backend.webgl.kernels.util import change_order, convert_position, simplify_orders, \
    texture_shape, texture_stride, convert_coord
from webdnn.graph.operators.reshape import Reshape
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util.misc import mul


def factorize(x, n=4):
    """
    factorize x with "n" factors
    """
    k = int(x ** (1 / n))
    while x % k != 0:
        k -= 1

    if n == 2:
        return x // k, k

    else:
        return factorize(x // k, n - 1) + (k,)


@WebGLDescriptorGenerator.register_handler(Reshape)
def reshape(op: Reshape) -> List[Kernel]:
    x = op.inputs["x"]
    y = op.outputs["y"]

    in_order = op.parameters["in_order"]

    out_order = op.parameters["out_order"]

    dummy_y = Variable(y.shape, y.order).change_order(out_order)
    orders_y_dy, shapes_y_dy = simplify_orders([y, dummy_y])
    if orders_y_dy[y] == orders_y_dy[dummy_y]:
        order = Order([None] * 4)
        shape = factorize(y.size)
        stride = [mul(shape[i + 1:]) for i in range(4)]
        dummy_y = Variable(y.shape, y.order)
        shapes_y_dy = {y: shape, dummy_y: shape}
        strides_y_dy = {y: stride, dummy_y: stride}
        orders_y_dy = {y: order, dummy_y: order}

    else:
        shapes_y_dy = {v: [shapes_y_dy[v][a] for a in orders_y_dy[v].axes] for v in [y, dummy_y]}
        strides_y_dy = {v: [mul(shapes_y_dy[v][i + 1:]) for i in range(orders_y_dy[v].ndim)] for v in [y, dummy_y]}

    dummy_x = Variable(x.shape, x.order).change_order(in_order)
    orders_x_dx, shapes_x_dx = simplify_orders([x, dummy_x])
    if orders_x_dx[x] == orders_x_dx[dummy_x]:
        order = Order([None] * 4)
        shape = factorize(x.size)
        stride = [mul(shape[i + 1:]) for i in range(4)]
        dummy_x = Variable(x.shape, x.order)
        shapes_x_dx = {x: shape, dummy_x: shape}
        strides_x_dx = {x: stride, dummy_x: stride}
        orders_x_dx = {x: order, dummy_x: order}

    else:
        shapes_x_dx = {v: [shapes_x_dx[v][a] for a in orders_x_dx[v].axes] for v in [x, dummy_x]}
        strides_x_dx = {v: [mul(shapes_x_dx[v][i + 1:]) for i in range(orders_x_dx[v].ndim)] for v in [x, dummy_x]}

    # FIXME: optimize
    # y -{change_order}-> dummy_y -{convert_position}-> dummy_x -{change_order}-> x

    code = KernelCode([f"""
void main() {{
    gl_FragColor.r = texture2D(""", x, """,""", convert_coord(
        change_order(
            convert_position(
                change_order(
                    convert_position("gl_FragCoord.yx", texture_shape(y)[:2], texture_stride(y)[:2], shapes_y_dy[y], strides_y_dy[y]),
                    orders_y_dy[y], orders_y_dy[dummy_y]
                ),
                shapes_y_dy[dummy_y], strides_y_dy[dummy_y], shapes_x_dx[dummy_x], strides_x_dx[dummy_x]
            ),
            orders_x_dx[dummy_x], orders_x_dx[x]
        ),
        shapes_x_dx[x], strides_x_dx[x], texture_shape(x)[:2][::-1], texture_stride(x)[:2][::-1]
    ), f""").r;
}}
"""], name=op.__class__.__name__)
    source = code.generate()
    return [Kernel(
        source,
        code.name,
        code.samplers,
        code.uniforms,
        y
    )]
