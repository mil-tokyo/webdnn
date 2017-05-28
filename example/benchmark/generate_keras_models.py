import os

from keras.applications import VGG16
from keras.applications import resnet50

os.makedirs('output/kerasjs/resnet50', exist_ok=True)
os.makedirs('output/kerasjs/vgg16', exist_ok=True)

model = resnet50.ResNet50(include_top=True, weights='imagenet')
model.save('output/kerasjs/resnet50/model.h5')
with open('output/kerasjs/resnet50/model.json', 'w') as f:
    f.write(model.to_json())

model = VGG16(include_top=True, weights='imagenet')
model.save('output/kerasjs/vgg16/model.h5')
with open('output/kerasjs/vgg16/model.json', 'w') as f:
    f.write(model.to_json())
