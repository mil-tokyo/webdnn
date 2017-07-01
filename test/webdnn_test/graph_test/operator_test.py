from webdnn.graph.operator import Operator
from webdnn.graph.order import OrderNHWC
from webdnn.graph.variable import Variable


def test_append_input():
    op = Operator("op")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)

    op.append_input("v1", v1)
    op.append_input("v2", v2)

    assert op.inputs["v1"] == v1
    assert op.inputs["v2"] == v2
    assert v1.input_to == {op}
    assert v2.input_to == {op}


def test_remove_input():
    op = Operator("op")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)

    op.append_input("v1", v1)
    op.append_input("v2", v2)
    op.remove_input(v1)

    assert "v1" not in op.inputs
    assert op.inputs["v2"] == v2
    assert v1.input_to == set()
    assert v2.input_to == {op}


def test_replace_input():
    op = Operator("op")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)

    op.append_input("v1", v1)
    op.replace_input(v1, v2)

    assert op.inputs["v1"] == v2
    assert v1.input_to == set()
    assert v2.input_to == {op}


def test_append_output():
    op = Operator("op")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)

    op.append_output("v1", v1)
    op.append_output("v2", v2)

    assert op.outputs["v1"] == v1
    assert op.outputs["v2"] == v2
    assert v1.output_from == op
    assert v2.output_from == op


def test_remove_output():
    op = Operator("op")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)

    op.append_output("v1", v1)
    op.append_output("v2", v2)
    op.remove_output(v1)

    assert "v1" not in op.outputs
    assert op.outputs["v2"] == v2
    assert v1.output_from is None
    assert v2.output_from == op


def test_replace_output():
    op = Operator("op")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)

    op.append_output("v1", v1)
    op.replace_output(v1, v2)

    assert op.outputs["v1"] == v2
    assert v1.output_from is None
    assert v2.output_from == op


def test_remove_all():
    op = Operator("op")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)
    v3 = Variable((1, 2, 3, 4), OrderNHWC)
    v4 = Variable((1, 2, 3, 4), OrderNHWC)

    op.append_input("v1", v1)
    op.append_input("v2", v2)
    op.append_output("v3", v3)
    op.append_output("v4", v4)

    op.remove_all()

    assert len(op.inputs) == 0
    assert len(op.outputs) == 0
    assert v1.input_to == set()
    assert v2.input_to == set()
    assert v3.output_from is None
    assert v4.output_from is None


def test_replace_all():
    op1 = Operator("op1")
    op2 = Operator("op2")
    v1 = Variable((1, 2, 3, 4), OrderNHWC)
    v2 = Variable((1, 2, 3, 4), OrderNHWC)

    op1.append_input("v1", v1)
    op1.append_output("v2", v2)

    op1.replace(op2)

    assert len(op1.inputs) == 0
    assert len(op1.outputs) == 0
    assert len(op2.inputs) == 1 and op2.inputs["v1"] == v1
    assert len(op2.outputs) == 1 and op2.outputs["v2"] == v2
    assert v1.input_to == {op2}
    assert v2.output_from == op2
