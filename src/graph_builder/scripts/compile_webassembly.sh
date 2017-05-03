#!/bin/bash

set -e # exit on error

emcc "$1" -O3 -s "EXPORTED_FUNCTIONS=['_run','_init','_get_weight_buffer','_get_data_buffer']" -s "WASM=1" --pre-js `dirname "$0"`/webassembly_header.js -o "${1%.*}.js"
