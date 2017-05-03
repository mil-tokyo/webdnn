#!/bin/bash

set -e # exit on error

emcc output/kernels_webassembly.c -s "EXPORTED_FUNCTIONS=['_run','_init','_get_weight_buffer','_get_data_buffer']" -s "WASM=1" -O3 -o kernels_webassembly.js
mv kernels_webassembly.js kernels_webassembly_footer.js
cat webassembly_header.js kernels_webassembly_footer.js > kernels_webassembly.js
