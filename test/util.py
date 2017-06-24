import atexit
import os.path as path
import shutil
from abc import abstractmethod
from typing import Type, Dict, List, Union, Iterable, Optional
from unittest import SkipTest

import numpy as np

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.graph.graph import Graph
from webdnn.graph.operator import Operator
from webdnn.graph.order import OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderCNHW, \
    OrderCHWN, OrderNCHW
from webdnn.graph.variable import Variable
from webdnn.util.json import json


def template_elementwise_operator(OperatorClass: Type[Operator], operator_kwargs: Optional[Dict[str, any]] = None):
    orders = [OrderC, OrderNC, OrderCN, OrderNHWC, OrderHWNC, OrderHWCN, OrderNCHW, OrderCNHW, OrderCHWN]

    for order in orders:
        op = OperatorClass("op", **(operator_kwargs or {}))

        x = Variable(np.arange(order.ndim) + 1, order)
        y, = op(x)
        for axis in y.order.axes:
            assert y.shape_dict[axis] == x.shape_dict[axis]


class FlagManager:
    _tmp_value = None

    def __init__(self, target_value: bool = True):
        self.target_value = target_value

    def setup(self):
        self._tmp_value = self.get()
        self.set(self.target_value)

    def teardown(self):
        self.set(self._tmp_value)

    @abstractmethod
    def get(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set(self, value: bool):
        raise NotImplementedError


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
                                  backend: Union[str, Iterable[str]],
                                  graph: Graph,
                                  inputs: Dict[Variable, np.array],
                                  expected: Dict[Variable, np.array],
                                  raise_skip: bool = True):
        """Generate test data for generated kernel codes
    
        Generated data are saved in JSON format, and BrowserTestRunner executes it.
        """

        if not cls.flag_initialized:
            cls.setup()

        if not isinstance(backend, str):
            for b in backend:
                generate_kernel_test_case(description, b, graph, inputs, expected, False)

            if raise_skip:
                raise SkipTest(f"[BrowserTest|{backend}] {description}")

            return

        graph_descriptor = generate_descriptor(backend, graph)

        testcase_dirname = f"testcase-{str(cls.counter)}"
        cls.counter += 1

        graph_descriptor.save(path.join(cls.OUTPUT_ROOT, testcase_dirname))

        cls.cases.append({
            "description": description,
            "inputs": [list(inputs[v].flatten()) for v in graph.inputs],
            "expected": [list(expected[v].flatten()) for v in graph.outputs],
            "dirname": testcase_dirname,
            "backend": backend
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
