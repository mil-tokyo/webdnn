import argparse
import os
from os import path
import sys
import ast

import PIL.Image
import chainer
import chainer.computational_graph
import chainer.links.caffe
import numpy as np

from graph_builder.backend.fallback.generator import generate as generate_fallback_descriptor
from graph_builder.backend.webgpu.generator import generate as generate_webgpu_descriptor
from graph_builder.frontend.general_optimize_rule import GeneralOptimizeRule
from graph_builder.graph.converters.chainer import ChainerGraphConverter
from graph_builder.graph.variable import Variable
from graph_builder.util.json import json

OUTPUT_DIR = path.join(path.dirname(__file__), "./output")


def main():
    parser = argparse.ArgumentParser()
    # default is Caffenet of Caffe example
    parser.add_argument("caffemodel", default="../../resources/caffemodel/bvlc_reference_caffenet.caffemodel")
    parser.add_argument("--backend", default="webgpu", choices=["webgpu", "fallback"])
    parser.add_argument("--shape", default="(1,3,227,227)")
    parser.add_argument("--sample_image")
    parser.add_argument("--input_name", default="data")
    parser.add_argument("--output_name", default="fc8")
    parser.add_argument("--optimize", action="store_true")
    parser.add_argument("--encoding")
    args = parser.parse_args()

    dummy_input_shape = ast.literal_eval(args.shape)  # (1,3,227,227)
    assert isinstance(dummy_input_shape, tuple)
    assert len(dummy_input_shape) == 4
    assert all(isinstance(o, int) for o in dummy_input_shape)
    if args.sample_image:
        sample_image = PIL.Image.open(args.sample_image)  # "../../resources/imagenet/ILSVRC2012_val_00000001.JPEG"
        assert dummy_input_shape[0:2] == (1, 3)
        resized = sample_image.resize(dummy_input_shape[2:4])
        input_data = np.asarray(resized).astype(np.float32, copy=True)
        input_data = input_data[:, :, ::-1]  # BGR
        input_data -= [103.939, 116.779, 123.68]  # mean
        input_data = np.transpose(input_data, (2, 0, 1))  # c,h,w
        input_data = input_data[np.newaxis, :, :, :]
    else:
        input_data = np.zeros(dummy_input_shape, dtype=np.float32)
    sys.stderr.write("Loading caffe model... (usually takes several minutes)\n")
    link = chainer.links.caffe.CaffeFunction(args.caffemodel)

    sys.stderr.write("Generating feedforward graph\n")
    nn_input = chainer.Variable(input_data)
    nn_output = link(inputs={args.input_name: nn_input}, outputs=[args.output_name], train=False)[0]
    chainer_cg = chainer.computational_graph.build_computational_graph([nn_output])
    converter = ChainerGraphConverter()
    graph = converter.convert(chainer_cg, [nn_input], [nn_output])  # type: Variable

    if args.optimize:
        sys.stderr.write("Optimizing graph\n")
        graph, _ = GeneralOptimizeRule().optimize(graph)

    sys.stderr.write("Generating descriptors\n")
    if args.backend == "webgpu":
        descriptor, data = generate_webgpu_descriptor(graph, constant_encoder_name=args.encoding)

    elif args.backend == "fallback":
        descriptor, data = generate_fallback_descriptor(graph, constant_encoder_name=args.encoding)

    else:
        raise NotImplementedError()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(path.join(OUTPUT_DIR, "image_nhwc.json".format()), "w") as f:
        image_nhwc = np.transpose(input_data, (0, 2, 3, 1))
        json.dump(image_nhwc.flatten().tolist(), f)

    with open(path.join(OUTPUT_DIR, "output.json".format()), "w") as f:
        json.dump(nn_output.data.tolist(), f)

    with open(path.join(OUTPUT_DIR, "graph_{}.json".format(args.backend)), "w") as f:
        json.dump(descriptor, f, indent=2)

    if args.backend == "webgpu":
        with open(path.join(OUTPUT_DIR, "kernels_{}.metal".format(args.backend)), "w") as f:
            f.write(descriptor.concat_kernel_sources())

    with open(path.join(OUTPUT_DIR, "weight_{}.bin".format(args.backend)), "wb") as f:
        f.write(data)

if __name__ == "__main__":
    main()
