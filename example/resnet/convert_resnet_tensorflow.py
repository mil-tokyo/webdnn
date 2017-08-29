"""
Example of converting ResNet-50 Tensorflow model

TODO:
clone https://github.com/tensorflow/models in output_tensorflow
wget and extract http://download.tensorflow.org/models/resnet_v1_50_2016_08_28.tar.gz in output_tensorflow

"""
import argparse
import numpy as np
import os
import tensorflow as tf

from webdnn.util import console

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

from tensorflow.contrib import slim
from webdnn.backend import generate_descriptor
from webdnn.frontend.tensorflow import TensorFlowConverter
import sys
sys.path.append("output_tensorflow/models/slim")
from nets import resnet_v1

def main():
    sys.setrecursionlimit(10000)

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="resnet50", choices=["resnet50"])
    parser.add_argument('--out', '-o', default='output_tensorflow',
                        help='Directory to output the graph descriptor')
    parser.add_argument("--encoding", help="name of weight encoder")
    parser.add_argument("--backend", default="webgpu,webgl,webassembly,fallback", help="backend")
    args = parser.parse_args()

    image_size = resnet_v1.resnet_v1.default_image_size

    checkpoints_dir = args.out
    sess = tf.Session()
    processed_images = tf.placeholder(tf.float32, [1, image_size, image_size, 3])

    # Create the model, use the default arg scope to configure the batch norm parameters.
    with slim.arg_scope(resnet_v1.resnet_arg_scope()):
        logits, _ = resnet_v1.resnet_v1_50(processed_images, num_classes=1000, is_training=False)
    probabilities = tf.nn.softmax(logits)

    init_fn = slim.assign_from_checkpoint_fn(
        os.path.join(checkpoints_dir, 'resnet_v1_50.ckpt'),
        slim.get_model_variables())

    init_fn(sess)

    graph = TensorFlowConverter(sess, batch_size=1).convert([processed_images], [probabilities])

    from webdnn.graph import traverse
    traverse.dump(graph)

    for backend in args.backend.split(","):
        graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
        graph_exec_data.save(args.out)

    console.stderr("Done.")


if __name__ == "__main__":
    main()
