# SqueezeNet

Example of [SqueezeNet](https://arxiv.org/abs/1602.07360)[landola+, 2016] image classification.

The model source code and pretrained model is from [https://github.com/wohlert/keras-squeezenet](https://github.com/wohlert/keras-squeezenet)

## Usage

1. Convert pretrained model by WebDNN

    ```bash
    $ python convert_keras.py
    ```

    Pre-trained model and converted data are stored under `/output_keras` directory.

2. Access `/webdnn/example/squeeze_net` in your browser. 
