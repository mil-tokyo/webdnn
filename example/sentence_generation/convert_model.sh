#!/bin/sh

python ../../bin/convert_keras.py output/lstm_text_generation.h5 --input_shape '(1,40,57)' --out output --backend webgpu,webassembly
