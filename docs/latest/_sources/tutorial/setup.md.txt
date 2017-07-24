# Setup guide (for Mac / Linux)

For Windows users, jump to [setup_windows](../setup_windows.html)

## Downloading code
```
git clone https://github.com/mil-tokyo/webdnn
```

## Installing WebGPU environment
WebDNN runs fastest on browsers which support WebGPU. Currently, only Safari Technology Preview on macOS supports it.

https://developer.apple.com/safari/technology-preview/

If you don't have such environment, WebAssembly backend can be used.
It is supported by most modern browsers.
(Note: IE and Safari does not support WebAssembly, but asm.js code is automatically generated along with WebAssembly code, and gives similar performance.)

## Installing python package
This framework requires python3.6+.

```
cd webdnn
python3 setup.py install
```

This will install `webdnn`.

If you want to convert models of Caffe or Chainer, install chainer package.

```
pip install chainer
```

(Currently, tested with `chainer==2.0` and  `chainer==1.23`)

## Installing Emscripten and Eigen
If you want to enable WebAssembly backend, em++ command from [Emscripten](https://github.com/kripken/emscripten) is required. You can skip this section if you try WebGPU backend only.

To setup Emscripten which supports WebAssembly,

```
git clone https://github.com/juj/emsdk.git
cd emsdk
./emsdk install sdk-incoming-64bit binaryen-master-64bit
./emsdk activate sdk-incoming-64bit binaryen-master-64bit
```
(see also http://webassembly.org/getting-started/developers-guide/ )

To enable em++ command, you need to type command on the shell.

```
source ./emsdk_env.sh
```

[Eigen](http://eigen.tuxfamily.org) is needed as the library.

```
wget http://bitbucket.org/eigen/eigen/get/3.3.3.tar.bz2
tar jxf 3.3.3.tar.bz2
```

To enable Eigen to be included on compile, you need to type command on the shell.

```
export CPLUS_INCLUDE_PATH=$PWD/eigen-eigen-67e894c6cd8f
```

## Notes on python environment
Emscripten requires `python2` command, you need to setup python environment which `python` (or `python3`) is python 3.6+ and `python2` is python 2.7. [pyenv](https://github.com/pyenv/pyenv) may help to setup such environment ([see also](https://github.com/pyenv/pyenv/blob/master/COMMANDS.md#pyenv-global-advanced)).
