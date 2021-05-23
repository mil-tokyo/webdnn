"""
Tool to extract subgraph of ONNX model for debug.
"""

import argparse
import numpy as np
import onnx
import onnxruntime
from webdnn.tensor_export import serialize_tensors

def parse_name_shapes(name_shapes: str):
    result = {}
    for name_shape in name_shapes.split(","):
        name, shape_str = name_shape.split("=")
        shape = tuple(map(int, shape_str.split("x")))
        result[name] = shape
    return result

def find_node_which_output(graph, output_name):
    for node in graph.node:
        for output in node.output:
            if output == output_name:
                return node
    return None

def collect_subgraph_nodes(graph, in_names, out_names, initializer_names):
    unresolved_tensors = list(out_names)
    resolved_tensors = set(in_names) | set(initializer_names)
    subgraph_nodes = []
    while len(unresolved_tensors) > 0:
        target = unresolved_tensors.pop()
        node = find_node_which_output(graph, target)
        if node is None:
            print(target)
            raise ValueError
        for input_name in node.input:
            if input_name not in resolved_tensors:
                unresolved_tensors.append(input_name)
        for output_name in node.output:
            resolved_tensors.add(output_name)
        if node not in subgraph_nodes:
            subgraph_nodes.append(node)
    return sort_subgraph_nodes(subgraph_nodes, in_names, initializer_names)

def sort_subgraph_nodes(nodes, in_names, initializer_names):
    resolved_tensors = set(in_names) | set(initializer_names)
    sorted_nodes = []
    unresolved_nodes = nodes.copy()
    while len(unresolved_nodes) > 0:
        for node in unresolved_nodes:
            if all(name in resolved_tensors for name in node.input):
                for name in node.output:
                    resolved_tensors.add(name)
                sorted_nodes.append(node)
                unresolved_nodes.remove(node)
                break
    return sorted_nodes

def collect_initializers(graph, subgraph_nodes):
    input_names = set()
    for n in subgraph_nodes:
        for in_name in n.input:
            input_names.add(in_name)
    filtered_initializers = []
    for init in graph.initializer:
        if init.name in input_names:
            filtered_initializers.append(init)
    return filtered_initializers

def replace_list(protobuf_list, new_items):
    while len(protobuf_list) > 0:
        protobuf_list.pop()
    for item in new_items:
        protobuf_list.append(item)

def process_model(model, input_shapes, output_shapes):
    graph = model.graph
    initializer_names = [initializer.name for initializer in graph.initializer]
    input_names = list(input_shapes.keys())
    output_names = list(output_shapes.keys())
    s_nodes = collect_subgraph_nodes(graph, input_names, output_names, initializer_names)
    f_initializers = collect_initializers(graph, s_nodes)
    replace_list(graph.node, s_nodes)
    replace_list(graph.initializer, f_initializers)
    replace_list(graph.input, [onnx.helper.make_tensor_value_info(name, onnx.TensorProto.FLOAT, shape) for name, shape in input_shapes.items()])
    replace_list(graph.output, [onnx.helper.make_tensor_value_info(name, onnx.TensorProto.FLOAT, shape) for name, shape in output_shapes.items()])

def make_test_io(model_path, output_shapes, test_input_shapes):
    test_inputs = {}
    session = onnxruntime.InferenceSession(model_path)
    for name, shape in test_input_shapes.items():
        test_inputs[name] = np.random.random(shape).astype(np.float32)
    output_names = list(output_shapes.keys())
    output_arrays = session.run(output_names, test_inputs)
    test_io_case = test_inputs
    for name, array in zip(output_names, output_arrays):
        test_io_case[name] = array
    return test_io_case

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", help="Source onnx model")
    parser.add_argument("dst", help="Destination onnx model")
    parser.add_argument("inputshapes", help="Input tensor names and shapes of subgraph. Example: 'tensor3=10x256,tensor4=-1x-1'")
    parser.add_argument("outputshapes", help="Output tensor names and shapes of subgraph. Example: 'tensor3=10x256,tensor4=-1x-1'")
    parser.add_argument("--test", help="Outputs test case file. Also needs --test-shapes")
    parser.add_argument("--test-shapes")
    args = parser.parse_args()
    input_shapes = parse_name_shapes(args.inputshapes)
    output_shapes = parse_name_shapes(args.outputshapes)
    model = onnx.load_model(args.src)
    process_model(model, input_shapes, output_shapes)
    try:
        onnx.checker.check_model(model)
    except Exception as ex:
        print("Checker error")
        print(ex)
    onnx.save_model(model, args.dst)
    print("Saved model")

    if args.test:
        test_shapes = parse_name_shapes(args.test_shapes)
        test_io_case = make_test_io(args.dst, output_shapes, test_shapes)
        serialize_tensors(args.test, test_io_case)
        print("Saved test io case")

if __name__ == "__main__":
    main()
