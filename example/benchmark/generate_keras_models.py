"""
Generate Keras model h5 files for using in benchmark
"""

import os
from argparse import ArgumentParser
from typing import Type, NamedTuple

from keras.applications import ResNet50, VGG16, InceptionV3
from keras.engine import Model


class ModelDesc(NamedTuple):
    name: str
    cls: Type[Model]


models = {
    "resnet50": ModelDesc(name="ResNet50", cls=ResNet50),
    "vgg16": ModelDesc(name="VGG16", cls=VGG16),
    "inception_v3": ModelDesc(name="InceptionV3", cls=InceptionV3)
}


def generate(key: str):
    if key not in models:
        raise KeyError(f"Unknown model: {key}")

    desc = models[key]
    root_path = f"./output/kerasjs/{key}"

    if os.environ.get(f"NO_{desc.name.upper()}", "0") == "1":
        print(f"It is skipped to generate {desc.name}" +
              f"because environment variable \"NO_{desc.name.upper()}\" is True")
        return

    if os.path.exists(f"{root_path}/model.h5") and os.path.exists(f"{root_path}/model.h5"):
        print(f"{desc.name} model data has been generated already in {root_path}/" +
              "model.{h5, json}. If you want regenerate it, please remove these files first.")
        return

    os.makedirs(root_path, exist_ok=True)
    model = desc.cls(include_top=True, weights="imagenet")
    model.save(f"{root_path}/model.h5")
    with open(f"{root_path}/model.json", "w") as f:
        f.write(model.to_json())


parser = ArgumentParser()
parser.add_argument("key", type=str, choices=list(models.keys()))
args = parser.parse_args()

generate(args.key)
