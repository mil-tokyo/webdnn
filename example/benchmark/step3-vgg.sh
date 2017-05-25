#!/bin/sh
set -e
set -x

cd keras-js
python encoder.py ../data/vgg16.hdf5
