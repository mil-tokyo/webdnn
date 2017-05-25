#!/bin/sh
set -e
set -x

cd keras-js
python encoder.py ../data/resnet50.hdf5
