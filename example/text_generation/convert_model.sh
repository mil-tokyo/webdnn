#!/bin/sh

mkdir -p output
wget https://github.com/mil-tokyo/webdnn-data/raw/master/models/lstm_text_generation/lstm_text_generation.h5 -O output/lstm_text_generation.h5
wget https://github.com/mil-tokyo/webdnn-data/raw/master/models/lstm_text_generation/model_setting.json -O output/model_setting.json
python ../../bin/convert_keras.py output/lstm_text_generation.h5 --input_shape '(1,40,57)' --out output --backend webgpu,webassembly
