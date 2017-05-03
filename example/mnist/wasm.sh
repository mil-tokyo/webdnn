#!/bin/sh
emcc output/kernels_webassembly.c -s "EXPORTED_FUNCTIONS=['_run','_init','_get_weight_buffer','_get_data_buffer']" -s "WASM=1" -o kernels_webassembly.js
