import numpy as np

from graph_transpiler.backend.webassembly.operators.im2col import Im2Col as WasmIm2Col
from graph_transpiler.backend.webgpu.operators.im2col import Im2Col as WebGPUIm2Col
from graph_transpiler.graph.graph import Graph
from graph_transpiler.graph.variable import Variable
from graph_transpiler.graph.variables.attributes.order import OrderNHWC, OrderCNHW
from graph_transpiler.graph.variables.constant_variable import ConstantVariable
from test.util import generate_kernel_test_case


def generate_data_311():
    v_im = np.array([[[
        [1, 2],
        [3, 4]
    ], [
        [5, 6],
        [7, 8]
    ]]]).astype(np.float)  # Order: NCHW
    v_im = np.rollaxis(v_im, 1, 4)  # Order: NHWC

    v_col = np.array([[[[[
        [0, 0, 0],
        [0, 1, 2],
        [0, 3, 4],
    ], [
        [0, 0, 0],
        [1, 2, 0],
        [3, 4, 0],
    ]], [[
        [0, 1, 2],
        [0, 3, 4],
        [0, 0, 0],
    ], [
        [1, 2, 0],
        [3, 4, 0],
        [0, 0, 0],
    ]]], [[[
        [0, 0, 0],
        [0, 5, 6],
        [0, 7, 8],
    ], [
        [0, 0, 0],
        [5, 6, 0],
        [7, 8, 0],
    ]], [[
        [0, 5, 6],
        [0, 7, 8],
        [0, 0, 0],
    ], [
        [5, 6, 0],
        [7, 8, 0],
        [0, 0, 0],
    ]]]]]).astype(np.float)  # Order: (N, C, H, W, KH, KW)
    v_col = np.rollaxis(v_col, 1, 6).reshape(1, 2, 2, 3 * 3 * 2)  # Order: NHWC

    return v_im, v_col


def generate_data_212():
    v_im = np.array([[[
        [1, 2],
        [3, 4]
    ], [
        [5, 6],
        [7, 8]
    ]]]).astype(np.float)  # Order: NCHW
    v_im = np.rollaxis(v_im, 1, 4)  # Order: NHWC

    v_col = np.array([[[[[
        [0, 0],
        [0, 1]
    ], [
        [0, 0],
        [2, 0]
    ]], [[
        [0, 3],
        [0, 0],
    ], [
        [4, 0],
        [0, 0]
    ]]], [[[
        [0, 0],
        [0, 5]
    ], [
        [0, 0],
        [6, 0]
    ]], [[
        [0, 7],
        [0, 0]
    ], [
        [8, 0],
        [0, 0],
    ]]]]]).astype(np.float)  # Order: (N, C, H, W, KH, KW)
    v_col = np.rollaxis(v_col, 1, 6).reshape(1, 2, 2, 2 * 2 * 2)  # Order: NHWC

    return v_im, v_col


def test_NHWC():
    v_im, v_col = generate_data_311()

    im = Variable(v_im.shape, order=OrderNHWC)

    col_wasm, = WasmIm2Col(None, ksize=3, padding=1, stride=1)(im)
    col_wasm.change_order(OrderNHWC)

    col_webgpu, = WebGPUIm2Col(None, ksize=3, padding=1, stride=1)(im)
    col_webgpu.change_order(OrderNHWC)

    generate_kernel_test_case(
        description=f"Im2Col output=NHWC",
        backend=["webassembly"],
        graph=Graph([im], [col_wasm]),
        inputs={im: v_im},
        expected={col_wasm: v_col},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Im2Col output=NHWC",
        backend=["webgpu"],
        graph=Graph([im], [col_webgpu]),
        inputs={im: v_im},
        expected={col_webgpu: v_col}
    )


def test_CNHW():
    v_im, v_col = generate_data_311()

    col_dummy = ConstantVariable(v_col, order=OrderNHWC)
    col_dummy.change_order(OrderCNHW)

    im = Variable(v_im.shape, order=OrderNHWC)

    col_wasm, = WasmIm2Col(None, ksize=3, padding=1, stride=1)(im)
    col_wasm.change_order(OrderCNHW)

    col_webgpu, = WebGPUIm2Col(None, ksize=3, padding=1, stride=1)(im)
    col_webgpu.change_order(OrderCNHW)

    generate_kernel_test_case(
        description=f"Im2Col output=CNHW",
        backend=["webassembly"],
        graph=Graph([im], [col_wasm]),
        inputs={im: v_im},
        expected={col_wasm: col_dummy.data},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Im2Col output=CNHW",
        backend=["webgpu"],
        graph=Graph([im], [col_webgpu]),
        inputs={im: v_im},
        expected={col_webgpu: col_dummy.data}
    )


def test_wide_stride_NHWC():
    v_im, v_col = generate_data_212()

    im = Variable(v_im.shape, order=OrderNHWC)

    col_wasm, = WasmIm2Col(None, ksize=2, padding=1, stride=2)(im)
    col_wasm.change_order(OrderNHWC)

    col_webgpu, = WebGPUIm2Col(None, ksize=2, padding=1, stride=2)(im)
    col_webgpu.change_order(OrderNHWC)

    generate_kernel_test_case(
        description=f"Im2Col output=NHWC stride=2",
        backend=["webassembly"],
        graph=Graph([im], [col_wasm]),
        inputs={im: v_im},
        expected={col_wasm: v_col},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Im2Col output=NHWC stride=2",
        backend=["webgpu"],
        graph=Graph([im], [col_webgpu]),
        inputs={im: v_im},
        expected={col_webgpu: v_col}
    )


def test_wide_stride_CNHW():
    v_im, v_col = generate_data_212()

    col_dummy = ConstantVariable(v_col, order=OrderNHWC)
    col_dummy.change_order(OrderCNHW)

    im = Variable(v_im.shape, order=OrderNHWC)

    col_wasm, = WasmIm2Col(None, ksize=2, padding=1, stride=2)(im)
    col_wasm.change_order(OrderCNHW)

    col_webgpu, = WebGPUIm2Col(None, ksize=2, padding=1, stride=2)(im)
    col_webgpu.change_order(OrderCNHW)

    generate_kernel_test_case(
        description=f"Im2Col output=CNHW stride=2",
        backend=["webassembly"],
        graph=Graph([im], [col_wasm]),
        inputs={im: v_im},
        expected={col_wasm: col_dummy.data},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Im2Col output=CNHW stride=2",
        backend=["webgpu"],
        graph=Graph([im], [col_webgpu]),
        inputs={im: v_im},
        expected={col_webgpu: col_dummy.data}
    )
