# Setup guide (for Windows)

No browser on Windows supports WebGPU, but you can still develop applications using WebDNN. Commands have to be used on command prompt.

## Downloading code
```
git clone https://github.com/mil-tokyo/webdnn
```

If you do not have git, zip file is also available: [https://github.com/mil-tokyo/webdnn/archive/master.zip](https://github.com/mil-tokyo/webdnn/archive/master.zip)

## Installing python environment
If you do not have python environment, install python environment.

Anaconda is the popular installer: [https://www.continuum.io/downloads](https://www.continuum.io/downloads)

When installing, adding PATH to system is optional.

This framework requires python3.6+. This document is based on Anaconda 4.4.0.

If you want to convert models of Caffe or Chainer, install chainer package. Refer to [Chainer document](http://docs.chainer.org/en/stable/install.html).

(Currently, tested with `chainer==2.0` and  `chainer==1.23`)

## Installing Emscripten and Eigen
If you want to enable WebAssembly backend, em++ command from [Emscripten](https://github.com/kripken/emscripten) is required. You can skip this section if you try WebGPU backend only.

To setup Emscripten which supports WebAssembly,

Download "Emscripten SDK Offline Installer (emsdk-1.35.0-full-64bit.exe)" from [http://kripken.github.io/emscripten-site/docs/getting_started/downloads.html](http://kripken.github.io/emscripten-site/docs/getting_started/downloads.html).

When installing, you should add PATH of `emcc` to PATH, but PATH of `python` should not be added (as it conflicts with Anaconda).

[Eigen](http://eigen.tuxfamily.org) is needed as the library. Download latest source from [http://eigen.tuxfamily.org/index.php?title=Main_Page](http://eigen.tuxfamily.org/index.php?title=Main_Page) and decompress.

## Setting for using proper python
python environment (3.6.x) of Anaconda have to be executed with `python3` command. To accompilsh it, create a file named `python3.bat` and fill with the following content.

```bat
"C:\ProgramData\Anaconda3\python.exe" %*
```

python environment (2.7.x) of Anaconda have to be executed with `python` command. To accompilsh it, create a file named `python.bat` and fill with the following content.

```bat
set CPLUS_INCLUDE_PATH=PATH\TO\EIGEN
"C:\Program Files\Emscripten\python\2.7.5.3_64bit\python.exe" %*
```

Concrete path depends on the version of Emscripten and installer configuration. `PATH\TO\EIGEN` have to be replaced by the directory where Eigen is downloaded. The file `PATH\TO\EIGEN\Eigen\Dense` should exists.

## Verification of Emscripten and Eigen installation
Create a file named `hello.cpp`:

```cpp
#include <Eigen/Dense>
#include <iostream>

int main()
{
  std::cout << "hello world" << std::endl;
  return 0;
}

```

Then, try to compile it into WebAssembly:

```bat
em++ hello.cpp -O3 -s WASM=1 -o hello.html
```

If Emscripten works well, files such as `hello.wasm`, `hello.html` are generated.

## Installing graph transpiler
Install graph transpiler for Anaconda python environment.

At the top directory of WebDNN is cloned, type

```bat
python3 setup.py install
```

Here, `python3.bat` have to exist on the current directory.

## Running example

```
cd example\mnist
python3 train_mnist_chainer.py
```

Here, `python3.bat`, `python.bat` have to exist on the current directory.

Graph descriptor files for each backend are generated.

In Emscripten 1.35, files `before.js`, `load-wasm-worker.js` seem to be generated on current directory (it seems that latest Emscripten for linux does not require them). You have to move them to the output directory.
