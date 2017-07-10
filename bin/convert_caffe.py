"""
Caffe model converter (via Chainer model)
"""

import argparse
import os
import sys
from os import path

import chainer
import chainer.computational_graph
import chainer.links.caffe
import numpy as np

from webdnn import Graph, Shape
from webdnn.backend import generate_descriptor
from webdnn.frontend.chainer import ChainerConverter
from webdnn.util import console


def parse_input_blob(args):
    input_filled = False
    if args.input_npy:
        input_array = np.load(args.input_npy)
        assert isinstance(input_array, np.ndarray)
        input_blob = chainer.Variable(input_array)
        input_filled = True  # input data is filled with meaningful data
    else:
        if not args.input_shape:
            raise ValueError("input_npy or input_shapes must be specified to determine input")
        input_shape, placeholders = Shape.parse(args.input_shape)
        if len(placeholders) > 0:
            raise ValueError("caffe converter does not support an input with placeholder")
        input_blob = chainer.Variable(np.zeros(input_shape, dtype=np.float32))
    return input_blob, input_filled


def main():
    sys.setrecursionlimit(10000)  # workaround for deep copying large graph
    parser = argparse.ArgumentParser()
    # default is Caffenet of Caffe example
    parser.add_argument("caffemodel")
    parser.add_argument("--backend", default="webgpu,webassembly,fallback",
                        help="comma-separated list of backends")
    parser.add_argument("--input_name",
                        help="blob name for input (mandatory)")
    parser.add_argument("--input_shape",
                        help="shape of blobs for inputs (example: '(1,3,224,224)')")
    parser.add_argument("--input_npy",
                        help="npy file containing sample inputs")
    parser.add_argument("--output_names", required=True,
                        help="comma-separated blob name for output (mandatory)")
    parser.add_argument("--out",
                        help="output directory (default: <model>/webdnn_graph_descriptor)")
    parser.add_argument("--encoding", help="name of weight encoder")
    args = parser.parse_args()

    # multiple blob input can be easily implemented, but command-line arguments becomes complicated.
    input_blob, input_filled = parse_input_blob(args)
    output_names = args.output_names.split(",")

    console.stderr("[convert_caffe] Loading caffe model... (usually takes several minutes)")
    link = chainer.links.caffe.CaffeFunction(args.caffemodel)

    console.stderr("[convert_caffe] Generating feedforward graph")
    if chainer.__version__ >= "2.":
        chainer.using_config("train", False)
        output_blobs = list(
            link(inputs={args.input_name: input_blob}, outputs=output_names))  # list of Variable
    else:
        output_blobs = list(
            link(inputs={args.input_name: input_blob}, outputs=output_names, train=False))  # list of Variable
    chainer_cg = chainer.computational_graph.build_computational_graph(output_blobs)
    converter = ChainerConverter()
    graph = converter.convert(chainer_cg, [input_blob], output_blobs)  # type: Graph

    if args.out:
        output_dir = args.out
    else:
        output_dir = path.join(path.dirname(args.caffemodel), "webdnn_graph_descriptor")
    os.makedirs(output_dir, exist_ok=True)

    if input_filled:
        # save output of Caffe Network (not required for inference)
        output_arrays = {output_name: output_blob.data for output_name, output_blob in zip(output_names, output_blobs)}
        np.savez(path.join(output_dir, "example_output.npz"), **output_arrays)

    console.stderr("[convert_caffe] Generating descriptors")
    any_backend_failed = False
    for backend in args.backend.split(","):
        try:
            graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
            graph_exec_data.save(output_dir)
        except Exception as ex:
            any_backend_failed = True
            console.error(f"[convert_caffe] Failed generating descriptor for backend {backend}: {str(ex)}")

    if any_backend_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
