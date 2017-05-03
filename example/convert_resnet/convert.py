import argparse
import os
from os import path

import PIL.Image
import chainer
import chainer.computational_graph
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
    parser.add_argument("--model", default="vgg16", choices=["vgg16", "resnet50"])
    parser.add_argument("--backend", default="webgpu", choices=["webgpu", "fallback"])
    parser.add_argument("--optimize", action="store_true")
    parser.add_argument("--encoding")
    args = parser.parse_args()

    sample_image = PIL.Image.open("../../resources/imagenet/ILSVRC2012_val_00000001.JPEG")

    if args.model == "vgg16":
        link = chainer.links.model.vision.vgg.VGG16Layers()
        prepared_image = chainer.links.model.vision.vgg.prepare(sample_image)  # BGR, CHW
        out_layer_name = "fc8"

    elif args.model == "resnet50":
        link = chainer.links.model.vision.resnet.ResNet50Layers()
        prepared_image = chainer.links.model.vision.resnet.prepare(sample_image)
        out_layer_name = "fc6"

    nn_input = chainer.Variable(np.array([prepared_image], dtype=np.float32))
    nn_output = link(nn_input, layers=[out_layer_name])[out_layer_name]  # 'prob' is also possible (uses softmax)
    chainer_cg = chainer.computational_graph.build_computational_graph([nn_output])
    converter = ChainerGraphConverter()
    graph = converter.convert(chainer_cg, [nn_input], [nn_output])  # type: Variable

    if args.optimize:
        graph, _ = GeneralOptimizeRule().optimize(graph)

    if args.backend == "webgpu":
        descriptor, data = generate_webgpu_descriptor(graph, constant_encoder_name=args.encoding)

    elif args.backend == "fallback":
        descriptor, data = generate_fallback_descriptor(graph, constant_encoder_name=args.encoding)

    else:
        raise NotImplementedError()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(path.join(OUTPUT_DIR, "image_nhwc.json".format()), "w") as f:
        image_nhwc = np.transpose(prepared_image, (1, 2, 0))
        json.dump(image_nhwc.flatten().tolist(), f)

    with open(path.join(OUTPUT_DIR, "fc6.json".format()), "w") as f:
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
