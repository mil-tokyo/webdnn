# Benchmark

The benchmark for computing speed of DNN model on web browser

**NOTE**

`/example/benchmark` measure the processing time including GPU-CPU transfer time. This benchmark measured the time without transfer time.

- Models
    - ResNet50

- Execution type
    - WebDNN (WebGL + Optimization)
    - deeplearn.js (GPU)

## How to run

1. run `convert.sh`.

    ```shell
    $ ./convert.sh
    ```
    
    This script do follows things:
    
    - Save Keras pretrained models
    - Convert pretrained models into WebDNN format

2. open `index.html` on your browser
