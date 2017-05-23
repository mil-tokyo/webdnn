#!/bin/sh

set -e
# This script is same as simple usage in caffenet_conversion.ipynb

if ! [ -f data/bvlc_reference_caffenet.caffemodel ]; then
echo "Downloading caffenet model (240MB)..."
wget http://dl.caffe.berkeleyvision.org/bvlc_reference_caffenet.caffemodel -P data
fi

# sample image, not necesasary for conversion itself
if ! wget "https://upload.wikimedia.org/wikipedia/commons/3/3b/1%2C0_KoShamo.jpg" -O "data/cock.jpg"; then
echo "Failed to load sample image, continuing to conversion"
fi

# check existence of commands
if ! which em++; then
echo "em++ command does not exist. Generating graph descriptor for webassembly will fail."
fi

if ! which python2; then
echo "python2 command does not exist. Generating graph descriptor for webassembly will fail."
fi

echo "Start model conversion"
python ../../bin/convert_caffe.py --input_name data --input_shape '(1,3,227,227)' --output_names fc8 --out output data/bvlc_reference_caffenet.caffemodel
