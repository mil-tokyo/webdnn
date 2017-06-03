import os
from typing import Type

from keras.applications import ResNet50, VGG16, InceptionV3
from keras.engine import Model


def generate(NetworkModel: Type[Model], name: str, root_path: str, ):
    if os.environ.get(f'NO_{name.upper()}', '0') == '1':
        print(f'It is skipped to generate {name}' +
              f'because environment variable "NO_{name.upper()}" is set')

    elif os.path.exists(f'{root_path}/model.h5') and os.path.exists(f'{root_path}/model.h5'):
        print(f'{name} model data has been generated already in {root_path}/' +
              'model.{h5, json}. If you want regenerate it, please remove these files first.')

    else:
        os.makedirs(root_path, exist_ok=True)
        model = NetworkModel(include_top=True, weights='imagenet')
        model.save(f'{root_path}/model.h5')
        with open(f'{root_path}/model.json', 'w') as f:
            f.write(model.to_json())


generate(ResNet50, 'ResNet50', './output/kerasjs/resnet50')
generate(VGG16, 'VGG16', './output/kerasjs/vgg16')
generate(InceptionV3, 'InceptionV3', './output/kerasjs/inception_v3')
