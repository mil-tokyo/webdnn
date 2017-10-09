"""
This source code is created based on https://github.com/wohlert/keras-squeezenet

---------------------------------------------------------------------------------------------------------------------------------------
https://github.com/wohlert/keras-squeezenet

MIT License

Copyright (c) 2016 Jesper Wohlert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from keras.layers import Convolution2D, MaxPooling2D, AveragePooling2D, Activation
from keras.layers import Input, Flatten, Dropout, Concatenate
from keras.models import Model
from keras.utils.data_utils import get_file

WEIGHTS_PATH = 'https://github.com/wohlert/keras-squeezenet/releases/download/v0.1/squeezenet_weights.h5'


def _fire(x, filters, name="fire"):
    sq_filters, ex1_filters, ex2_filters = filters
    squeeze = Convolution2D(sq_filters, (1, 1), activation='relu', padding='same', name=name + "/squeeze1x1")(x)
    expand1 = Convolution2D(ex1_filters, (1, 1), activation='relu', padding='same', name=name + "/expand1x1")(squeeze)
    expand2 = Convolution2D(ex2_filters, (3, 3), activation='relu', padding='same', name=name + "/expand3x3")(squeeze)
    y = Concatenate(axis=-1, name=name)([expand1, expand2])
    return y


def SqueezeNet():
    x = Input(shape=(223, 223, 3))

    h = Convolution2D(64, kernel_size=(3, 3), strides=(2, 2), padding="same", activation="relu", name='conv1')(x)
    h = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='maxpool1', padding="valid")(h)

    h = _fire(h, (16, 64, 64), name="fire2")
    h = _fire(h, (16, 64, 64), name="fire3")

    h = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='maxpool3', padding="valid")(h)

    h = _fire(h, (32, 128, 128), name="fire4")
    h = _fire(h, (32, 128, 128), name="fire5")

    h = MaxPooling2D(pool_size=(2, 2), strides=(2, 2), name='maxpool5', padding="valid")(h)

    h = _fire(h, (48, 192, 192), name="fire6")
    h = _fire(h, (48, 192, 192), name="fire7")

    h = _fire(h, (64, 256, 256), name="fire8")
    h = _fire(h, (64, 256, 256), name="fire9")

    h = Convolution2D(1000, (1, 1), padding='valid', name='conv10')(h)
    h = AveragePooling2D(pool_size=(14, 14), name='avgpool10')(h)
    h = Flatten(name='flatten10')(h)
    h = Activation("softmax", name='softmax')(h)

    model = Model(x, h, name="squeezenet")
    model.load_weights(get_file('squeezenet_weights.h5', WEIGHTS_PATH, cache_subdir='models'))
    return model
