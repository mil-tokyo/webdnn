"""
This source code is created based on https://github.com/yusuketomoto/chainer-fast-neuralstyle/blob/master/net.py

---------------------------------------------------------------------------------------------------------------------------------------
https://github.com/yusuketomoto/chainer-fast-neuralstyle

The MIT License (MIT)

Copyright (c) 2016 Yusuke Tomoto

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

import math

import chainer
import chainer.functions as F
import chainer.links as L

if chainer.__version__ >= "2.":
    class ResidualBlock(chainer.Chain):
        def __init__(self, n_in, n_out, stride=1, ksize=3):
            w = math.sqrt(2)
            super(ResidualBlock, self).__init__(
                c1=L.Convolution2D(n_in, n_out, ksize, stride, 1, initialW=chainer.initializers.Normal(w / math.sqrt(n_in))),
                c2=L.Convolution2D(n_out, n_out, ksize, 1, 1, initialW=chainer.initializers.Normal(w / math.sqrt(n_in))),
                b1=L.BatchNormalization(n_out),
                b2=L.BatchNormalization(n_out)
            )

        # noinspection PyCallingNonCallable, PyUnresolvedReferences
        def __call__(self, x):
            h = F.relu(self.b1(self.c1(x)))
            h = self.b2(self.c2(h))
            if x.data.shape != h.data.shape:
                xp = chainer.cuda.get_array_module(x.data)
                n, c, hh, ww = x.data.shape
                pad_c = h.data.shape[1] - c
                p = xp.zeros((n, pad_c, hh, ww), dtype=xp.float32)
                p = chainer.Variable(p)
                x = F.concat((p, x))
                if x.data.shape[2:] != h.data.shape[2:]:
                    x = F.average_pooling_2d(x, 1, 2)
            return h + x


    class FastStyleNet(chainer.Chain):
        def __init__(self):
            super(FastStyleNet, self).__init__(
                c1=L.Convolution2D(3, 32, 9, stride=1, pad=4),
                c2=L.Convolution2D(32, 64, 4, stride=2, pad=1),
                c3=L.Convolution2D(64, 128, 4, stride=2, pad=1),
                r1=ResidualBlock(128, 128),
                r2=ResidualBlock(128, 128),
                r3=ResidualBlock(128, 128),
                r4=ResidualBlock(128, 128),
                r5=ResidualBlock(128, 128),
                d1=L.Deconvolution2D(128, 64, 4, stride=2, pad=1),
                d2=L.Deconvolution2D(64, 32, 4, stride=2, pad=1),
                d3=L.Deconvolution2D(32, 3, 9, stride=1, pad=4),
                b1=L.BatchNormalization(32),
                b2=L.BatchNormalization(64),
                b3=L.BatchNormalization(128),
                b4=L.BatchNormalization(64),
                b5=L.BatchNormalization(32),
            )

        # noinspection PyCallingNonCallable, PyUnresolvedReferences
        def __call__(self, x):
            h = self.b1(F.elu(self.c1(x)))
            h = self.b2(F.elu(self.c2(h)))
            h = self.b3(F.elu(self.c3(h)))
            h = self.r1(h)
            h = self.r2(h)
            h = self.r3(h)
            h = self.r4(h)
            h = self.r5(h)
            h = self.b4(F.elu(self.d1(h)))
            h = self.b5(F.elu(self.d2(h)))
            y = self.d3(h)
            return (F.tanh(y) + 1) * 127.5

else:

    class ResidualBlock(chainer.Chain):
        def __init__(self, n_in, n_out, stride=1, ksize=3):
            w = math.sqrt(2)
            super(ResidualBlock, self).__init__(
                c1=L.Convolution2D(n_in, n_out, ksize, stride, 1, w),
                c2=L.Convolution2D(n_out, n_out, ksize, 1, 1, w),
                b1=L.BatchNormalization(n_out),
                b2=L.BatchNormalization(n_out)
            )

        # noinspection PyCallingNonCallable, PyUnresolvedReferences
        def __call__(self, x, test):
            h = F.relu(self.b1(self.c1(x), test=test))
            h = self.b2(self.c2(h), test=test)
            if x.data.shape != h.data.shape:
                xp = chainer.cuda.get_array_module(x.data)
                n, c, hh, ww = x.data.shape
                pad_c = h.data.shape[1] - c
                p = xp.zeros((n, pad_c, hh, ww), dtype=xp.float32)
                p = chainer.Variable(p, volatile=test)
                x = F.concat((p, x))
                if x.data.shape[2:] != h.data.shape[2:]:
                    x = F.average_pooling_2d(x, 1, 2)
            return h + x


    class FastStyleNet(chainer.Chain):
        def __init__(self):
            super(FastStyleNet, self).__init__(
                c1=L.Convolution2D(3, 32, 9, stride=1, pad=4),
                c2=L.Convolution2D(32, 64, 4, stride=2, pad=1),
                c3=L.Convolution2D(64, 128, 4, stride=2, pad=1),
                r1=ResidualBlock(128, 128),
                r2=ResidualBlock(128, 128),
                r3=ResidualBlock(128, 128),
                r4=ResidualBlock(128, 128),
                r5=ResidualBlock(128, 128),
                d1=L.Deconvolution2D(128, 64, 4, stride=2, pad=1),
                d2=L.Deconvolution2D(64, 32, 4, stride=2, pad=1),
                d3=L.Deconvolution2D(32, 3, 9, stride=1, pad=4),
                b1=L.BatchNormalization(32),
                b2=L.BatchNormalization(64),
                b3=L.BatchNormalization(128),
                b4=L.BatchNormalization(64),
                b5=L.BatchNormalization(32),
            )

        # noinspection PyCallingNonCallable, PyUnresolvedReferences
        def __call__(self, x, test=True):
            h = self.b1(F.elu(self.c1(x)), test=test)
            h = self.b2(F.elu(self.c2(h)), test=test)
            h = self.b3(F.elu(self.c3(h)), test=test)
            h = self.r1(h, test=test)
            h = self.r2(h, test=test)
            h = self.r3(h, test=test)
            h = self.r4(h, test=test)
            h = self.r5(h, test=test)
            h = self.b4(F.elu(self.d1(h)), test=test)
            h = self.b5(F.elu(self.d2(h)), test=test)
            y = self.d3(h)
            return (F.tanh(y) + 1) * 127.5
