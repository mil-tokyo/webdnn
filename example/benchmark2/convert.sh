#!/bin/sh

set -e

echo "Generate Keras model"
python3 generate_keras_models.py

echo ""
echo "Encode Keras model into WebDNN model:"
OPTIMIZE=1 python3 ../../bin/convert_keras.py keras_model/model.h5 \
    --input_shape '(1,224,224,3)' \
    --out webdnn_model
