"""
Example of converting ResNet-50 Keras model
"""

import argparse
import sys
import os
from os import path
import subprocess

from keras.applications import resnet50


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="resnet50", choices=["resnet50"])
    parser.add_argument('--out', '-o', default='output_keras',
                        help='Directory to output the graph descriptor')
    parser.add_argument("--encoding", help="name of weight encoder")

    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("Exporting Keras model into file")
    model = resnet50.ResNet50(include_top=True, weights='imagenet')
    model.save(path.join(args.out, "resnet50.h5"))


    print("Converting model into WebDNN format (graph descriptor)")
    # only for demo purpose, maybe not safe
    convert_keras_command = f"python ../../bin/convert_keras.py {args.out}/resnet50.h5 --input_shape '(1,224,224,3)' --out {args.out}"
    if args.encoding:
        convert_keras_command += f" --encoding {args.encoding}"
    print("$ " + convert_keras_command)

    subprocess.check_call(convert_keras_command, shell=True)

    print("Done.")

if __name__ == "__main__":
    main()
