import numpy as np

from test.util import generate_kernel_test_case
from webdnn.backend.webassembly.operators.col2im import Col2Im as WasmCol2Im
from webdnn.backend.webgpu.operators.col2im import Col2Im as WebGPUCol2Im
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def generate_data_311():
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
    v_col /= 4

    v_im = np.array([[[
        [1, 2],
        [3, 4]
    ], [
        [5, 6],
        [7, 8]
    ]]]).astype(np.float)  # Order: NCHW
    v_im = np.rollaxis(v_im, 1, 4)  # Order: NHWC

    return v_im, v_col


def generate_data_212():
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

    v_im = np.array([[[
        [1, 2],
        [3, 4]
    ], [
        [5, 6],
        [7, 8]
    ]]]).astype(np.float)  # Order: NCHW
    v_im = np.rollaxis(v_im, 1, 4)  # Order: NHWC

    return v_im, v_col


def test_NHWC():
    v_im, v_col = generate_data_311()

    col = Variable(v_col.shape, order=OrderNHWC)

    im_wasm, = WasmCol2Im(None, ksize=3, padding=1, stride=1)(col)
    im_wasm.change_order(OrderNHWC)

    im_webgpu, = WebGPUCol2Im(None, ksize=3, padding=1, stride=1)(col)
    im_webgpu.change_order(OrderNHWC)

    generate_kernel_test_case(
        description=f"Col2Im output=NHWC",
        backend=["webassembly"],
        graph=Graph([col], [im_wasm]),
        inputs={col: v_col},
        expected={im_wasm: v_im},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Col2Im output=NHWC",
        backend=["webgpu"],
        graph=Graph([col], [im_webgpu]),
        inputs={col: v_col},
        expected={im_webgpu: v_im},
    )


def test_wide_stride_NHWC():
    v_im, v_col = generate_data_212()

    col = Variable(v_col.shape, order=OrderNHWC)

    im_wasm, = WasmCol2Im(None, ksize=2, padding=1, stride=2)(col)
    im_wasm.change_order(OrderNHWC)

    im_webgpu, = WebGPUCol2Im(None, ksize=2, padding=1, stride=2)(col)
    im_webgpu.change_order(OrderNHWC)

    generate_kernel_test_case(
        description=f"Col2Im output=NHWC stride=2",
        backend=["webassembly"],
        graph=Graph([col], [im_wasm]),
        inputs={col: v_col},
        expected={im_wasm: v_im},
        raise_skip=False
    )

    generate_kernel_test_case(
        description=f"Col2Im output=NHWC stride=2",
        backend=["webgpu"],
        graph=Graph([col], [im_webgpu]),
        inputs={col: v_col},
        expected={im_webgpu: v_im},
    )
