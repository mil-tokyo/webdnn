# Docker container of webdnn

## Example usage

### Create container
```
docker run -it --name webdnn-container -p 8000:8000 -v /path/to/webdnn:/root/mount milhidaka/webdnn
```

The following commands are supposed to be run inside container.

Deep learning package for your model have to be installed (not included because they are very large).

### Tensorflow
```
pip3 install tensorflow==1.12.0
```

### Keras (Tensorflow backend)

```
pip3 install tensorflow==1.12.0 keras==2.2.4
```

### Chainer
```
pip3 install chainer==4.4.0
```

### PyTorch
```
pip3 install http://download.pytorch.org/whl/cpu/torch-0.4.1-cp36-cp36m-linux_x86_64.whl torchvision==0.2.1 onnx==1.3.0
```

### Convert example model

```
cd /root/mount/example/mnist
python3 train_mnist_tensorflow.py
```

(`tensorflow` changes if you installed another framework.)

Note: you will see the following warning, but it is expected because `xcrun` is only in mac OS.
```
Warning: [WebGPUDescriptorGenerator] 'xcrun' command is not found. validation of generated source code in webgpu backend is skipped.
```

### Run example on web browser
Run HTTP server on the container.

```
cd /root/mount
python3 -m http.server
```

Now, you can see the example from web browser in the host by accessing [http://localhost:8000/example/mnist](http://localhost:8000/example/mnist).
