"""
Keras model converter
"""

import argparse
import ast
import os
import sys
import traceback
from os import path

import h5py

from webdnn.backend.interface.generator import generate_descriptor
from webdnn.graph.converters.keras import KerasConverter
from webdnn.util import flags, console


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
    args = parser.parse_args()

    console.stderr(f"[{path.basename(__file__)}] Generating feedforward graph")

    input_shape = ast.literal_eval(args.input_shape)
    input_shapes = [input_shape]
    model = h5py.File(args.kerasmodel, "r")
    converter = KerasConverter()
    graph = converter.convert(model, input_shapes)

    if args.out:
        output_dir = args.out
    else:
        output_dir = path.join(path.dirname(args.kerasmodel), "webdnn_graph_descriptor")
    os.makedirs(output_dir, exist_ok=True)

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
