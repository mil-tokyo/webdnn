#!/bin/sh

set -e

echo "Generate Keras model"
python generate_keras_models.py

echo ""
echo "Encode Keras model into Keras.js model:"
if [ ! -e ./kerasjs ]; then
git clone https://github.com/transcranial/keras-js.git kerasjs
fi
cd kerasjs
python encoder.py ../output/kerasjs/resnet50/model.h5
python encoder.py ../output/kerasjs/vgg16/model.h5
python encoder.py ../output/kerasjs/inception_v3/model.h5
cd -

echo ""
echo "Encode Keras model into WebDNN model:"
OPTIMIZE=0 python ../../bin/convert_keras.py output/kerasjs/resnet50/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/resnet50/non_optimized
OPTIMIZE=1 python ../../bin/convert_keras.py output/kerasjs/resnet50/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/resnet50/optimized
OPTIMIZE=0 python ../../bin/convert_keras.py output/kerasjs/vgg16/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/vgg16/non_optimized
OPTIMIZE=1 python ../../bin/convert_keras.py output/kerasjs/vgg16/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/vgg16/optimized
OPTIMIZE=0 python ../../bin/convert_keras.py output/kerasjs/inception_v3/model.h5 \
    --input_shape '(1,299,299,3)' \
    --out output/webdnn/inception_v3/non_optimized
OPTIMIZE=1 python ../../bin/convert_keras.py output/kerasjs/inception_v3/model.h5 \
    --input_shape '(1,299,299,3)'\
    --out output/webdnn/inception_v3/optimized
