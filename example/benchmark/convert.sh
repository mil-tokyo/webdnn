#!/bin/sh

set -e

# Check If Keras.js is cloned already
if [ ! -e ./keras-js ]; then
    echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
    echo "\033[0;36m  Keras.js repository is cloned: \033[0;31mNo\033[0;39m"
    echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
    git clone https://github.com/transcranial/keras-js keras-js
    cd keras-js
    git checkout 722df511c14e9aff03a56e3b2e1e657660b4a3c7
    cd -
    echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
    echo "\033[0;36m  Keras.js repository is cloned: \033[0;32mOK\033[0;39m"
    echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
else
    echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
    echo "\033[0;36m  Keras.js repository is cloned: \033[0;32mOK\033[0;39m"
    echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
fi

# Generate Keras model data
echo ""
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
echo "\033[0;36m  Generate Keras model"
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
python generate_keras_models.py
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
echo "\033[0;36m  Generate Keras model: \033[0;32mOK\033[0;39m"
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"

# Encode Keras model into Keras.js model
echo ""
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
echo "\033[0;36m  Encode Keras model into Keras.js model:"
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
cd ./keras-js
python encoder.py ../output/kerasjs/resnet50/model.h5
python encoder.py ../output/kerasjs/vgg16/model.h5
python encoder.py ../output/kerasjs/inception_v3/model.h5
cd -
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
echo "\033[0;36m  Encode Keras model into Keras.js model: \033[0;32mOK\033[0;39m"
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"

# Encode Keras model into WebDNN model
echo ""
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
echo "\033[0;36m  Encode Keras model into WebDNN model:"
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
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
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"
echo "\033[0;36m  Encode Keras model into WebDNN model: \033[0;32mOK\033[0;39m"
echo "\033[0;36m----------------------------------------------------------------\033[0;39m"

