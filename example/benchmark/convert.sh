#!/bin/sh

set -e

echo "Generate Keras model"
pip3 install -r ./requirements_kerasjs.txt
python3 generate_keras_models.py

echo ""
echo "Encode Keras model into Keras.js model:"
if [ ! -e ./kerasjs ]; then
git clone https://github.com/transcranial/keras-js.git kerasjs
cd kerasjs && git reset --hard a43f7a5a348e45f7a525e19952e232b123d85af1 && cd ..
fi
cd kerasjs
python3 ./python/encoder.py ../output/kerasjs/resnet50/model.h5
python3 ./python/encoder.py ../output/kerasjs/vgg16/model.h5
python3 ./python/encoder.py ../output/kerasjs/inception_v3/model.h5
cd -

echo ""
echo "Encode Keras model into WebDNN model:"
pip3 install -r ./requirements_webdnn.txt
OPTIMIZE=0 python3 ../../bin/convert_keras.py output/kerasjs/resnet50/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/resnet50/non_optimized
OPTIMIZE=1 python3 ../../bin/convert_keras.py output/kerasjs/resnet50/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/resnet50/optimized
OPTIMIZE=0 python3 ../../bin/convert_keras.py output/kerasjs/vgg16/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/vgg16/non_optimized
OPTIMIZE=1 python3 ../../bin/convert_keras.py output/kerasjs/vgg16/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out output/webdnn/vgg16/optimized
OPTIMIZE=0 python3 ../../bin/convert_keras.py output/kerasjs/inception_v3/model.h5 \
    --input_shape '(1,299,299,3)' \
    --out output/webdnn/inception_v3/non_optimized
OPTIMIZE=1 python3 ../../bin/convert_keras.py output/kerasjs/inception_v3/model.h5 \
    --input_shape '(1,299,299,3)'\
    --out output/webdnn/inception_v3/optimized
