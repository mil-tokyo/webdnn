import atexit
import os.path as path
import shutil
from typing import Dict, List
from unittest import SkipTest

import numpy as np

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.graph import traverse
from webdnn.graph.axis import Axis, AxisKeyDict
from webdnn.graph.graph import Graph
from webdnn.graph.order import OrderNC
from webdnn.graph.variable import Variable
from webdnn.util import flags
from webdnn.util.json import json


def assert_shape(v: Variable, expected: AxisKeyDict[int]):
    """assert_shape(v, expected)

    Assert variable shape is correct. If shape is mismatched, exception with information message is raised.

    Args:
        v: target variable
        expected: dictionary with key of axis and value of corresponding dimensions' size

    Examples

        >>> x = Variable((2, 3), OrderNC)
        >>> assert_shape(x, AxisKeyDict([Axis.N, Axis.C], [2, 3]))
        # no exception is raised.

        >>> assert_shape(x, AxisKeyDict([Axis.C, Axis.N], [2, 3]))
        "AssertionError: Shape mismatch: (expected shape)={N: 3, C: 2}, (real shape)={N: 2, C: 3}"

    """
    assert all(axis in v.order.axes for axis in expected.keys()) and all(axis in expected for axis in v.order.axes), \
        f"Shape mismatch: (expected shape)={expected}, (real shape)={v.shape_dict}"

    for axis in v.order.axes:
        assert v.shape_dict[axis] == expected[axis], \
            f"Shape mismatch: (expected shape)={expected}, (real shape)={v.shape_dict}"


def wrap_template(fn, arg_name="description"):
    """
    Decorator to inject information about custom configuration of test case.

    Args:
        fn (Callable): test case template
        arg_name (str): name of custom configuration information string

    Examples:

    ..code::

        template("custom_data")
        def template(a: float = 1.0, b: int = 1, custom_data: str = ""):

            # build your test

            generate_kernel_test_case(
                description=f"Example {custom_data}",
                graph=graph,
                inputs=inputs,
                expected=outputs
            )

        def test_1():
            template()  # generated test-case's description is "Example"

        def test_2():
            template(a=2.0)  # "Example a=2.0"

        def test_3():
            template(a=2.0, b=1)  # "Example a=2.0, b=1"

    Returns:
        wrapped template function
    """

    def wrapper(*args, **kwargs):
        kwargs[arg_name] = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        return fn(*args, **kwargs)

    return wrapper


class KernelTestCaseGenerator:
    OUTPUT_ROOT: str = path.join(path.dirname(__file__), "../build/test")
    cases: List[Dict[str, any]] = []
    flag_initialized = False
    counter = 0

    @classmethod
    def setup(cls):
        if path.exists(cls.OUTPUT_ROOT):
            shutil.rmtree(cls.OUTPUT_ROOT)

        cls.flag_initialized = True

    @classmethod
    def generate_kernel_test_case(cls,
                                  description: str,
                                  graph: Graph,
                                  inputs: Dict[Variable, np.array],
                                  expected: Dict[Variable, np.array],
                                  backend=None,
                                  raise_skip: bool = True,
                                  EPS: float = 1.0e-3,
                                  ABS_EPS: float = 0.0):
        """Generate test data for generated kernel codes
    
        Generated data are saved in JSON format, and BrowserTestRunner executes it.
        """

        if not cls.flag_initialized:
            cls.setup()

        if backend is None:
            backend = ["webgpu", "webgl", "webassembly", "fallback"]

        if not isinstance(backend, str):
            for b in backend:
                generate_kernel_test_case(
                    description=description,
                    graph=graph,
                    inputs=inputs,
                    expected=expected,
                    backend=b,
                    raise_skip=False,
                    EPS=EPS,
                    ABS_EPS=ABS_EPS)

            if raise_skip:
                raise SkipTest(f"[BrowserTest|{backend}] {description}")

            return

        backend_flag_map = {
            "webgpu": flags.test.TEST_WEBGPU,
            "webgl": flags.test.TEST_WEBGL,
            "webassembly": flags.test.TEST_WEBASSEMBLY,
            "fallback": flags.test.TEST_FALLBACK
        }

        if not backend_flag_map[backend]:
            return

        graph_descriptor = generate_descriptor(backend, graph)

        cls.counter += 1
        testcase_dirname = f"testcase-{str(cls.counter)}"

        output_root = path.join(cls.OUTPUT_ROOT, testcase_dirname)
        graph_descriptor.save(output_root)
        with open(path.join(output_root, "./cg.dot"), "w") as f:
            f.write(traverse.dump_dot(graph_descriptor.graph))

        cls.cases.append({
            "description": description,
            "inputs": [list(inputs[v].flatten()) for v in graph.inputs],
            "expected": [list(expected[v].flatten()) for v in graph.outputs],
            "dirname": testcase_dirname,
            "backend": backend,
            "EPS": EPS,
            "ABS_EPS": ABS_EPS
        })

        if raise_skip:
            raise SkipTest(f"[BrowserTest|{backend}] {description}")

    @classmethod
    def clean_up_callback(cls):
        if len(cls.cases) == 0:
            return

        with open(path.join(cls.OUTPUT_ROOT, "./master.json"), "w") as f:
            json.dump(cls.cases, f)


atexit.register(KernelTestCaseGenerator.clean_up_callback)
generate_kernel_test_case = KernelTestCaseGenerator.generate_kernel_test_case
