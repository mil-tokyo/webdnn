import os
from keras.applications import resnet50

os.makedirs('output/kerasjs/resnet50', exist_ok=True)

model = resnet50.ResNet50(include_top=True, weights='imagenet')
model.save_weights('output/kerasjs/resnet50/model.hdf5')
with open('output/kerasjs/resnet50/model.json', 'w') as f:
    f.write(model.to_json())
