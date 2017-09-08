# Benchmark

The benchmark for computing speed of DNN model on web browser

- Models
    - ResNet50
    - VGG16
    - Inception-v3

- Execution type
    - WebDNN (WebGPU + Optimization)
    - WebDNN (WebGPU)
    - WebDNN (WebGL + Optimization)
    - WebDNN (WebGL)
    - WebDNN (WebAssembly + Optimization)
    - WebDNN (WebAssembly)
    - Keras.js (GPU)
    - Keras.js (CPU)
    - deeplearn.js (GPU) (Only ResNet50 is supported)
    - deeplearn.js (CPU) (Only ResNet50 is supported)

## How to run

1. run `convert.sh`.

    ```shell
    $ ./convert.sh
    ```
    
    This script do follows things:
    
    - Clone Keras.js repository if need.
    - Save Keras pretrained models
    - Convert pretrained models into Keras.js format
    - Convert pretrained models into WebDNN format

2. open `index.html` on your browser
