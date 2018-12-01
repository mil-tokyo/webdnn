# Setup guide (for Windows)

No browser on Windows supports WebGPU, but you can still develop applications using WebDNN. Commands have to be used on command prompt.

## Downloading code
```
git clone https://github.com/mil-tokyo/webdnn
```

If you do not have git, zip file is also available: [https://github.com/mil-tokyo/webdnn/archive/master.zip](https://github.com/mil-tokyo/webdnn/archive/master.zip)

Once you learn how to use WebDNN and want to use it in your project, [npm](../../tips/npm.html) and [pip](../../tips/pip.html) packages may be useful (please note that they does not contain examples).

## Installing python environment
If you do not have python environment, install python environment.

Anaconda is the popular installer: [https://www.continuum.io/downloads](https://www.continuum.io/downloads)

When installing, adding PATH to system is optional.

This framework requires python3.6+. This document is based on Anaconda 4.4.0.

If you want to convert models of Caffe or Chainer, install chainer package. Refer to [Chainer document](http://docs.chainer.org/en/stable/install.html).

(Currently, tested with `chainer==4.4.0`)

## Installing Emscripten and Eigen
If you want to enable WebAssembly backend, em++ command from [Emscripten](https://github.com/kripken/emscripten) is required. You can skip this section if you try WebGPU backend only.

To setup Emscripten which supports WebAssembly, follow the official page [http://kripken.github.io/emscripten-site/docs/getting_started/downloads.html](http://kripken.github.io/emscripten-site/docs/getting_started/downloads.html).

Please note that "Emscripten SDK Offline Installer (emsdk-1.35.0-full-64bit.exe)" is too old because WebDNN uses options only avaliable on newer versions.

Please note that `emsdk_env.bat` have to be run every time.

[Eigen](http://eigen.tuxfamily.org) is needed as the library. Download latest source from [http://eigen.tuxfamily.org/index.php?title=Main_Page](http://eigen.tuxfamily.org/index.php?title=Main_Page) and decompress.

Move `Eigen` directory into `emsdk/emscripten/*/system/include`. * is version number of emscripten. The file `include/Eigen/Dense` have to exist.

## Setting for using proper python
python environment (3.6.x) of Anaconda have to be executed with `python3` command. To accompilsh it, create a file named `python3.bat` and fill with the following content.

```bat
"C:\ProgramData\Anaconda3\python.exe" %*
```

The actual path depends on your Anaconda installation. This is needed because `emsdk_env.bat` overwrites `python` to Emscripten's python 2.7.

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

```bat
python3 -m pip install webdnn
```

Here, `python3.bat` have to exist on the current directory.

## Running example

```
cd example\mnist
python3 train_mnist_chainer.py
```

Here, `python3.bat` have to exist on the current directory.

Graph descriptor files for each backend are generated.
