#!/usr/bin/env python

from keras.applications import resnet50

model = resnet50.ResNet50(include_top=True, weights='imagenet')
model.save_weights('data/resnet50.hdf5')
with open('data/resnet50.json', 'w') as f:
    f.write(model.to_json())
