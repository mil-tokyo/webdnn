#!/bin/sh

set -e

# Check If Keras.js is cloned already
if [ ! -e ./keras-js ]; then
    echo "Keras.js repository is cloned: \033[0;31mNo\033[0;39m"
    git clone https://github.com/transcranial/keras-js keras-js
    cd keras-js
    git checkout 722df511c14e9aff03a56e3b2e1e657660b4a3c7
    cd -
else
    echo "Keras.js repository is cloned: \033[0;32mOK\033[0;39m"
fi
echo "----------------------------------------------------------------"

# Generate Keras model data
echo ""
echo "Generate Keras model"
echo "----------------------------------------------------------------"
python generate_keras_models.py
echo "----------------------------------------------------------------"
echo "Generate Keras model: \033[0;32mOK\033[0;39m"

# Encode Keras model into Keras.js model
echo ""
echo "\033[sEncode Keras model into Keras.js model:"
cd ./keras-js
python encoder.py ../output/kerasjs/resnet50/model.hdf5
cd -
echo "\033[uEncode Keras model into Keras.js model: \033[0;32mOK\033[0;39m"

