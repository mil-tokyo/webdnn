"""
Example of converting ResNet-50 Tensorflow model
"""
import argparse
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
import subprocess

SLIM_GITHUB = "https://github.com/tensorflow/models"
SLIM_COMMIT = "09a32f3"
PRETRAINED_MODEL_URL = "http://download.tensorflow.org/models/resnet_v1_50_2016_08_28.tar.gz"
PRETRAINED_MODEL_FILENAME = "resnet_v1_50.ckpt"


def clone_slim(out_dir):
    console.stderr(f"Git cloning {SLIM_GITHUB} into {out_dir}...")
    subprocess.check_call(["git", "clone", SLIM_GITHUB, "models"], cwd=out_dir)
    subprocess.check_call(["git", "checkout", SLIM_COMMIT], cwd=os.path.join(out_dir, './models'))


def download_model(out_dir):
    import urllib
    model_dir = os.path.join(out_dir, "pretrained_model")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    model_path = os.path.join(model_dir, PRETRAINED_MODEL_FILENAME)
    if not os.path.exists(model_path):
        console.stderr(f"Downloading ResNet pretrained model...")
        tgz_filename, _ = urllib.request.urlretrieve(PRETRAINED_MODEL_URL)
        console.stderr(f"Extracting ResNet pretrained model (tar.gz)...")
        subprocess.check_call(["tar", "xf", tgz_filename], cwd=model_dir)
        os.remove(tgz_filename)
    else:
        console.stderr(f"Using already downloaded pretrained model {model_path}")
    return model_path


def generate_graph(output_root):
    os.makedirs(output_root, exist_ok=True)

    slim_dir = os.path.join(output_root, "models/slim")
    if not os.path.exists(slim_dir):
        clone_slim(output_root)

    sys.path.append(slim_dir)
    from nets import resnet_v1
    image_size = resnet_v1.resnet_v1.default_image_size

    with slim.arg_scope(resnet_v1.resnet_arg_scope()):
        x = tf.placeholder(tf.float32, [1, image_size, image_size, 3])
        logits, _ = resnet_v1.resnet_v1_50(x, num_classes=1000, is_training=False)
        y = tf.nn.softmax(logits)

    model_path = download_model(output_root)
    sess = tf.Session()
    slim.assign_from_checkpoint_fn(model_path, slim.get_model_variables())(sess)

    graph = TensorFlowConverter(sess, batch_size=1).convert([x], [y])
    return sess, x, y, graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', '-o', default='output_tensorflow', help='Directory to output the graph descriptor')
    parser.add_argument("--encoding", help="name of weight encoder")
    parser.add_argument("--backend", default="webgpu,webgl,webassembly,fallback", help="backend")
    args = parser.parse_args()

    _, _, _, graph = generate_graph(args.out)

    for backend in args.backend.split(","):
        graph_exec_data = generate_descriptor(backend, graph, constant_encoder_name=args.encoding)
        graph_exec_data.save(args.out)

    console.stderr("Done.")


if __name__ == "__main__":
    main()
