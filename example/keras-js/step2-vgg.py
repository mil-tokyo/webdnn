#!/usr/bin/env python

from keras.applications import VGG16

model = VGG16(include_top=True, weights='imagenet')
model.save_weights('data/vgg16.hdf5')
with open('data/vgg16.json', 'w') as f:
    f.write(model.to_json())
