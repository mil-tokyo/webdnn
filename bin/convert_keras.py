"""
Keras model converter
"""

import argparse
import importlib.util
import os
import sys
import traceback
from os import path

import keras

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.frontend.keras import KerasConverter
from webdnn.graph.placeholder import Placeholder
from webdnn.graph.shape import Shape
from webdnn.graph.traverse import dump_dot
from webdnn.util import flags, console


def _load_plugin(filepath: str):
    spec = importlib.util.spec_from_file_location("_plugin", filepath)
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)


def main():
    sys.setrecursionlimit(10000)  # workaround for deep copying large graph
    parser = argparse.ArgumentParser()
    parser.add_argument("kerasmodel")
    parser.add_argument("--backend", default="webgpu,webassembly,fallback",
                        help="comma-separated list of backends")
    parser.add_argument("--input_shape", required=True,
                        help="shape of blobs for inputs (example: '(1,3,224,224)')")
    # parser.add_argument("--input_data_format", choices=["channels_first", "channels_last"])
    parser.add_argument("--out",
                        help="output directory (default: <model>/webdnn_graph_descriptor)")
    parser.add_argument("--encoding", help="name of weight encoder")
    parser.add_argument("--visualize_ir", action="store_true")
    parser.add_argument("--plugin", action="append", help="plugin python files which are imported before transpiling")
    args = parser.parse_args()

    console.stderr(f"[{path.basename(__file__)}] Generating feedforward graph")
    if args.plugin:
        for plugin_path in args.plugin:
            _load_plugin(plugin_path)

    input_shape, _ = Shape.parse(args.input_shape)
    input_shapes = [input_shape]

    model = keras.models.load_model(args.kerasmodel)
    converter = KerasConverter()
    graph = converter.convert(model)

    for graph_input, input_shape in zip(graph.inputs, input_shapes):
        for p1, p2 in zip(graph_input.shape, input_shape):
            if not Placeholder.check_resolved(p1) and Placeholder.check_resolved(p2):
                p1.value = Placeholder.force_int(p2)

            elif Placeholder.check_resolved(p1) and not Placeholder.check_resolved(p2):
                raise ValueError(f'Shape mismatch: {p1} != {p2}')

            elif Placeholder.check_resolved(p1) and Placeholder.check_resolved(p2):
                assert p1 == p2, f'Shape mismatch: {p1} != {p2}'

    if args.out:
        output_dir = args.out
    else:
        output_dir = path.join(path.dirname(args.kerasmodel), "webdnn_graph_descriptor")
    os.makedirs(output_dir, exist_ok=True)

    if args.visualize_ir:
        ir_dot_path = path.join(output_dir, "ir.dot")
        with open(ir_dot_path, "w") as f:
            f.write(dump_dot(graph))
        console.stderr(f"IR graph can be visualized with graphviz command: 'dot {ir_dot_path} -T png -o output.png'")

    console.stderr(f"[{path.basename(__file__)}] Generating graph descriptor")

    any_backend_failed = False
    backends = args.backend.split(",")
    for i, backend in enumerate(backends):
        console.stderr(f"[{path.basename(__file__)}] Backend: {console.colorize(backend, console.Color.Cyan)}")
        try:
            graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
            graph_exec_data.save(output_dir)
        except Exception as ex:
            if flags.DEBUG:
                raise ex

            any_backend_failed = True
            console.error(f"[{path.basename(__file__)}] Failed generating descriptor for {backend} backend")
            console.stderr(traceback.format_exc())
            continue

    if any_backend_failed:
        exit(1)
        # raise last_backend_exception


if __name__ == "__main__":
    main()
