[![CircleCI](https://circleci.com/gh/mil-tokyo/webdnn.svg?style=svg)](https://circleci.com/gh/mil-tokyo/webdnn)

# WebDNN: Fastest DNN Execution Framework on Web Browser

**WebDNN** is an open source software framework for executing deep neural network (DNN) pre-trained model on web browser.

- [Japanese(日本語) README](https://github.com/mil-tokyo/webdnn/blob/master/README_ja.md)
- [website](https://mil-tokyo.github.io/webdnn)
- [document](https://mil-tokyo.github.io/webdnn/docs)

WebDNN can execute DNN models trained by follow deep learning frameworks on web browser.

- [TensorFlow](https://github.com/tensorflow/tensorflow) (`v1.2.0` - `v1.4.0`)
- [Keras](https://github.com/fchollet/keras) (`v2.1.3` - )
- [PyTorch](https://github.com/pytorch/pytorch) (`v0.3.0`)
- [Chainer](https://github.com/chainer/chainer) (`v1.23.0` - `v3.1.0`)
- [Caffe](https://github.com/BVLC/caffe)

# Why is WebDNN needed?

Deep neural network (DNN) is getting much attention to use in many applications. However, 
it requires a lot of computational resources, and there are many tremendous processes to 
setup execution environment based hardware acceleration such as GPGPU. Therefore providing 
DNN applications to end-users is very hard. 

**WebDNN** solves this problem by using web browser as installation-free DNN execution 
framework. This framework optimizes trained DNN model to compress the model data and 
accelerate the execution, and executes it with novel JavaScript API such as WebAssembly 
and WebGPU to achieve zero-overhead execution. Empirical evaluations showed that it 
achieved more than 200x acceleration.

# Performance

- Compared processing time with [Keras.js](https://github.com/transcranial/keras-js)
- Test environment: 
    - Mac Book Pro early 2015
    - macOS 10.12.4 Sierra
    - Intel Core i5 2.7 GHz CPU
    - 16 GB Memory
    - Intel Iris Graphics 6100 GPU
    - Safari Technology Preview 30
- Model: VGG16[[1]](#1), Inception-v3[[4]](#4), and ResNet50[[2]](#2). 
- Input Shape: `(1, 299, 299, 3)` for Inception-v3, `(1, 224, 224, 3)` for others.

![Benchmark result with Keras.js](https://github.com/mil-tokyo/webdnn/blob/master/docs/misc/performance.png)

Elapsed time per image are shown in vertical axis as logarithmic scale.

WebDNN with WebGPU backend was significantly faster than Keras.js. 
WebDNN with WebAssembly backend was comparable with GPU backend of Keras.js.
In each DNN model and backend, WebDNN obtained better results in terms of speed.
More speed improvement is observed when the optimizations are applied in the graph transpiler. 

# Getting started in 30 seconds

Let's convert and execute ResNet50 pre-trained Keras model[[3]](#3) on your web browser.

First, save ResNet50 pre-trained model provided by Keras.

```python
from keras.applications import resnet50
model = resnet50.ResNet50(include_top=True, weights='imagenet')
model.save("resnet50.h5")
```

Next, convert the model by CLI. In this phase, model is optimized.

```bash
python ./bin/convert_keras.py resnet50.h5 --input_shape '(1,224,224,3)' --out output
```

Then, generated files (called as `Descriptor`) can be loaded and executed by JavaScript as follows,

```js
let runner, image, probabilities;

async function init() {
    // Initialize descriptor runner
    runner = await WebDNN.load('./output');
    image = runner.inputs[0]; 
    probabilities = runner.outputs[0];
}

async function run() {
    // Set the value into input variable.
    image.set(await WebDNN.Image.getImageArray('./input_image.png'));
    
    // Run
    await runner.run(); 

    // Show the result
    console.log('Output', WebDNN.Math.argmax(probabilities));
}
```

WebDNN also supports Caffemodel and Chainer model.

For more information, please see [documents](https://mil-tokyo.github.io/webdnn/docs).

# Setup

Please see [documents](https://mil-tokyo.github.io/webdnn/docs/tutorial/setup.html).

# Applications / demos using WebDNN
- [http://make.girls.moe/#/](http://make.girls.moe/#/) - MakeGirls.moe - Create Anime Characters with A.I.!
- [https://milhidaka.github.io/chainer-image-caption/](https://milhidaka.github.io/chainer-image-caption/) - Generating image caption demo
- [https://github.com/milhidaka/webdnn-exercise](https://github.com/milhidaka/webdnn-exercise) - Exercise of basic usage of WebDNN

---

- <i id=1></i>[1] Karen Simonyan and Andrew Zisserman. 2014. Very Deep Convolutional Networks for Large-Scale Image Recognition. 
    In Proceedings of the International Conference on Learning Representations (ICLR).
- <i id=2></i>[2] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. 2015. Deep Residual
    Learning for Image Recognition. In Proceedings of the Conference on Computer Vision and Pattern Recognition (CVPR). 
    [https://github.com/KaimingHe/deep-residual-networks](https://github.com/KaimingHe/deep-residual-networks)
- <i id=3></i>[3] [Applications - Keras Documentation](https://keras.io/ja/applications/#resnet50)
- <i id=4></i>[4] Christian Szegedy, Vincent Vanhoucke, Sergey Ioffe, Jon Shlens, and Zbigniew Wojna. 2016.
    Rethinking the Inception Architecture for Computer Vision. In Proceedings of the Conference on Computer Vision and Pattern Recognition (CVPR).
