import re
from collections import namedtuple
from typing import List, Dict, Tuple, Set

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.command_buffer import CommandBuffer
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.graph import traverse
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.operators.elementwise import Elementwise
from webdnn.graph.order import Order
from webdnn.graph.variable import Variable
from webdnn.util import flags
from webdnn.util.misc import mul

RegisteredItem = namedtuple('RegisteredItem', ['OperatorClass', 'code', 'parameters'])


def _simplify_orders(variables: List[Variable]) -> Tuple[Dict[Variable, Order], Dict[Variable, AxisKeyDict[int]]]:
    """
    Simplify variable orders based on follow rules

    - Axis whose size is :code:`1` will be removed.

    - If axis :code:`A` and :code:`B` is adjacent in all variables which has axis :code:`A` and axis :code:`B`, :code:`A` and :code:`B` will
      be merged.
        - For example, :code:`OrderABC` and :code:`OrderCAB` can be simplified as :code:`OrderXC` and :code:`OrderCX`
        - In this case, the size of axis :code:`X` is calculated as :code:`(size of axis A) * (size of axis B)`

    ...code-block::text

        ex)
            x0.order=NHWC,  simplify    x0.order=X
             y.order=NHWC ------------>  y.order=X

        ex)
            x0.order=C,     simplify    x0.order=C
            x1.order=NHWC ------------> x1.order=XC
             y.order=NHWC                y.order=XC

        ex)
            x0.order=C,     simplify    x0.order=C
            x1.order=HW   ------------> x1.order=X
             y.order=NHWC                y.order=NXC

    Returns:
        (tuple of dicts) simplified orders and shape
    """

    orders = {}  # type: Dict[Variable, Order]
    shape_dicts = {}  # type: Dict[Variable, AxisKeyDict[int]]
    axis_scalar = Axis("Scalar")

    # remove all axes whose size is `1`.
    for v in variables:
        new_axes = [a for a in v.order.axes if v.shape_dict[a] != 1]
        orders[v] = Order(new_axes)
        shape_dicts[v] = AxisKeyDict(new_axes, [v.shape_dict[a] for a in new_axes])

        if len(new_axes) == 0 and v.size == 1:
            orders[v] = Order([axis_scalar])
            shape_dicts[v] = AxisKeyDict([(axis_scalar, 1)])

    # list up all axes and variables which have the axis
    var_dict = AxisKeyDict[Set[Variable]]()
    for v in variables:
        for axis in orders[v].axes:
            if axis in var_dict:
                var_dict[axis].add(v)
            else:
                var_dict[axis] = {v}

    # find pair of axes which can be merged
    counter = 0
    flag_continue = True
    while flag_continue:
        flag_continue = False

        for axis1, vars1 in list(var_dict.items()):
            for axis2, vars2 in list(var_dict.items()):
                if axis1 == axis2:
                    continue

                if vars1 != vars2 or any(orders[v].axes_dict[axis1] + 1 != orders[v].axes_dict[axis2] for v in vars1):
                    # `axis1` and `axis2` must be adjacent.
                    continue

                # merge `axis1` and `axis2` into `axis_new`

                axis_new = Axis(f"X{counter}")
                counter += 1

                for v in vars1:
                    shape_dict = shape_dicts[v]
                    shape_dict[axis_new] = shape_dict[axis1] * shape_dict[axis2]
                    del shape_dict[axis1]
                    del shape_dict[axis2]

                    order = orders[v]
                    orders[v] = Order(order.axes[:order.axes_dict[axis1]] + (axis_new,) + order.axes[order.axes_dict[axis2] + 1:])

                var_dict[axis_new] = vars1
                del var_dict[axis1]
                del var_dict[axis2]

                flag_continue = True
                break

            if flag_continue:
                break

    return orders, shape_dicts


def _optimize_loop_structure(variables: List[Variable]):
    """
    Optimize loop structure to iterate each element in variables

    Returns:
        (tuple): three elements are returned

        - First element is dictionary of orders with key of each variable and value of each variable's order. This order is
        simplified to avoid unnecessary deep loop.
        - Second element is shape dictionary of all variables.
        - The last element is stride dictionary of all variables.
    """
    orders, shape_dicts = _simplify_orders(variables)
    shapes = {v: [shape_dicts[v][a] for a in orders[v].axes] for v in variables}
    strides = {v: [mul(shapes[v][i + 1:]) for i in range(orders[v].ndim)] for v in variables}
    stride_dicts = {v: AxisKeyDict(orders[v].axes, strides[v]) for v in variables}

    # re-ordering
    axes = []
    for v in sorted(variables, key=lambda v: orders[v].ndim):
        axes += [axis for axis in orders[v].axes if axis not in axes]

    orders = {v: Order(list(filter(lambda x: x in orders[v].axes, axes))) for v in variables}

    return orders, shape_dicts, stride_dicts


_v_unique_counter = 0


def _generate_unique_name():
    global _v_unique_counter
    _v_unique_counter += 1
    return f"v{_v_unique_counter}"


def _reset_unique_counter():
    global _v_unique_counter
    _v_unique_counter = 0


# noinspection PyShadowingNames
def generate_elementwise_command_buffer(ops: List[Elementwise],
                                        items: List[RegisteredItem],
                                        memory_layout: MemoryLayout,
                                        dummy2real: Dict[Variable, Variable] = None):
    _reset_unique_counter()

    xs = set()  # type: Set[Variable]
    ys = set()  # type: Set[Variable]
    for op in ops:
        xs.update(op.inputs.values())
        ys.update(op.outputs.values())

    hidden_counter = xs.intersection(ys)
    xs = list(xs.difference(hidden_counter))  # type: List[Variable]
    ys = list(ys.difference(hidden_counter))  # type: List[Variable]

    assert len(ys) == 1, f"multi output: ys={ys}"
    y = ys[0]
    xs = traverse.sort_nodes(xs)  # type: List[Variable]

    orders, shape_dicts, stride_dicts = _optimize_loop_structure(xs + [y])
    iterate_order = orders[y]
    buffer_injector = BufferInjector()
    buffer = CommandBuffer(buffer_injector)

    name2variable = {}  # type: Dict[str, Variable]
    variable2name = {}  # type: Dict[Variable, str]
    variable2constant_name = {}  # type: Dict[Variable, str]
    variable2stride_name = {}  # type: Dict[Variable, List[str]]
    variable2buffer_name = {}  # type: Dict[Variable, str]

    """
    head declaration
    - buffer: X0, X1, ..., Y
    - variable stride: s_x0_0, s_x0_1, ...
    - loop size: D0, D1, D2, ...

    ex: c++)
        const device float *X0 = %%LOAD_BUFFER(elementwise_X0)%%
        device float *Y = %%LOAD_BUFFER(elementwise_Y)%%
        const int s_x0_0 = %%LOAD_BUFFER(elementwise_X0_stride_0)%%
        const int s_y_0 = %%LOAD_BUFFER(elementwise_Y_stride_0)%%
        const int s_y_1 = %%LOAD_BUFFER(elementwise_Y_stride_1)%%

        const int D1 = %%LOAD_BUFFER(elementwise_loop_size_1)%%
        const int D0 = %%LOAD_BUFFER(elementwise_loop_size_0)%%

    ex: code)

        (load, "const deice float *", "X0", "elementwise_X0")
        (load, "deice float *", "Y", "elementwise_Y")
        (load, "const int", "s_x0_0", "elementwise_X0_0)
        (load, "const int", "s_y_0", "elementwise_Y_0)
        (load, "const int", "s_y_1", "elementwise_Y_1)

        (load, "const int", "D0", "elementwise_loop_size_0")
        (load, "const int", "D1", "elementwise_loop_size_1")
    """
    for i, x in enumerate(xs):
        if flags.DEBUG:
            if i != 0:
                buffer.comment(f"")
            buffer.comment(f"{x}")

        name = _generate_unique_name()
        buffer.load(name, memory_layout[dummy2real[x] if dummy2real is not None and x in dummy2real else x], "float *", const=True)
        variable2buffer_name[x] = name

    if flags.DEBUG:
        buffer.comment(f"")
        buffer.comment(f"{y}")
    name = _generate_unique_name()
    buffer.load(name, memory_layout[dummy2real[y] if dummy2real is not None and y in dummy2real else y], "float *")
    variable2buffer_name[y] = name

    for x in xs:
        variable2stride_name[x] = []
        for d, axis2 in enumerate(iterate_order.axes):
            if axis2 not in stride_dicts[x] or stride_dicts[x][axis2] == 1:
                variable2stride_name[x].append("")
                continue

            name = _generate_unique_name()
            buffer.load(name, stride_dicts[x][axis2], "int", const=True)
            variable2stride_name[x].append(name)

    variable2stride_name[y] = []
    for d, axis2 in enumerate(iterate_order.axes):
        if axis2 not in stride_dicts[y] or stride_dicts[y][axis2] == 1:
            variable2stride_name[y].append("")
            continue

        name = _generate_unique_name()
        buffer.load(name, stride_dicts[y][axis2], "int", const=True)
        variable2stride_name[y].append(name)

    for i, axis in enumerate(iterate_order.axes):
        name = f"D{i}"
        buffer.load(name, shape_dicts[y][axis], "int", const=True)

    # open loop

    xs = list(sorted(xs, key=lambda x: orders[x].ndim))
    for i, axis in enumerate(iterate_order.axes):
        # FIXME: 一般化
        if iterate_order.ndim == 1:
            initial_value = "%%INITIAL_PARALLEL_POSITION%%"
            step_value = "%%PARALLEL_SIZE%%"

        else:
            T2 = 8
            if i == iterate_order.ndim - 2:
                initial_value = f"((%%PARALLEL_SIZE%% > {T2}) ? (%%INITIAL_PARALLEL_POSITION%% % (%%PARALLEL_SIZE%% / {T2})) : 0)"
                step_value = f"((%%PARALLEL_SIZE%% > {T2}) ? (%%PARALLEL_SIZE%% / {T2}) : 1)"

            elif i == iterate_order.ndim - 1:
                initial_value = f"((%%PARALLEL_SIZE%% > {T2}) ? (%%INITIAL_PARALLEL_POSITION%% / (%%PARALLEL_SIZE%% / {T2})) : 0)"
                step_value = f"((%%PARALLEL_SIZE%% > {T2}) ? {T2} : 1)"

            else:
                initial_value = "0"
                step_value = "1"

        buffer.declare(f"d{i}", "int")
        buffer.enterFor(f"d{i}", initial_value, f"D{i}", step_value)

        if i < iterate_order.ndim - 1:
            for x in xs:
                if axis not in orders[x].axes:
                    continue

                if orders[x].axes[-1] != axis:
                    continue

                name = _generate_unique_name()
                buffer_name = variable2buffer_name[x]

                expression = []
                for d, axis2 in enumerate(iterate_order.axes[:i + 1]):
                    if axis2 not in orders[x].axes:
                        continue

                    # FIXME: インデックス計算の最適化
                    if stride_dicts[x][axis2] == 1:
                        expression.append(f"d{d}")
                    else:
                        expression.append(f"d{d}*{variable2stride_name[x][d]}")

                if len(expression) == 0:
                    expression.append("0")

                buffer.declare(name, "float", f"{buffer_name}[{' + '.join(expression)}]", const=True)
                name2variable[name] = x
                variable2constant_name[x] = name

    # loop body
    for op, item in zip(ops, items):
        if flags.DEBUG:
            buffer.comment(f"{op}")

        var_mapping = {}  # type: Dict[str, str]

        # xs
        for name, x in sorted(op.inputs.items(), key=lambda keyval: keyval[1].name):
            if x in variable2constant_name:
                # use constant variable
                var_mapping[name] = variable2constant_name[x]

            elif x in variable2name:
                # use other variable
                var_mapping[name] = variable2name[x]

            else:
                new_name = _generate_unique_name()
                var_mapping[name] = new_name

                # load from buffer
                buffer_name = variable2buffer_name[x]
                expression = []
                for d, axis2 in enumerate(iterate_order.axes):
                    if axis2 not in orders[x].axes:
                        continue

                    # FIXME: インデックス計算の最適化
                    if stride_dicts[x][axis2] == 1:
                        expression.append(f"d{d}")
                    else:
                        expression.append(f"d{d}*{variable2stride_name[x][d]}")

                if len(expression) == 0:
                    expression.append("0")

                buffer.declare(new_name, "float", initial_value=f"{buffer_name}[{' + '.join(expression)}]", const=True)
                name2variable[new_name] = x
                variable2name[x] = new_name

        # y
        name = "y"
        y = op.outputs["y"]
        new_name = _generate_unique_name()
        var_mapping[name] = new_name
        buffer.declare(new_name, "float")
        name2variable[new_name] = y
        variable2name[y] = new_name

        # parameters
        buffer.enterBlockScope()
        for varname, fn in item.parameters.items():
            value = fn(op)

            # FIXME: cache
            if isinstance(value, float):
                buffer.load(varname, value, "float", const=True)

            elif isinstance(value, int):
                buffer.load(varname, value, "int", const=True)

            else:
                raise TypeError(f"Unsupported type: {type(value)}")

        # body
        body_expression = item.code
        for key, value in var_mapping.items():
            reg = re.compile("([^a-zA-Z_$]|^)(" + key + ")([^a-zA-Z_$]|$)", re.MULTILINE)
            pos = 0

            while True:
                ma = reg.search(body_expression, pos)
                if ma is None:
                    break

                span = ma.span()
                body_expression = body_expression[:span[0] + len(ma.group(1))] + value + body_expression[span[1] - len(ma.group(3)):]
                pos = span[0] + len(ma.group(1)) + len(value)

        buffer.exec(body_expression)

        buffer.exitBlockScope()

    # store final result
    y = ops[-1].outputs["y"]
    buffer_name = variable2buffer_name[y]
    expression = []
    for d in range(orders[y].ndim):
        # FIXME: インデックス計算の最適化
        if stride_dicts[y][orders[y].axes[d]] == 1:
            expression.append(f"d{d}")

        else:
            stride_name = variable2stride_name[y][d]
            expression.append(f"d{d}*{stride_name}")

    if len(expression) == 0:
        expression.append('0')

    buffer.exec(f"{buffer_name}[{' + '.join(expression)}] = {variable2name[y]};")

    # close loop
    for _ in list(enumerate(iterate_order.axes)):
        buffer.exitFor()

    return buffer, buffer_injector
