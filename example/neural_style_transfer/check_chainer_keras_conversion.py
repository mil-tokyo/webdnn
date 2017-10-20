import numpy as np
from keras.models import Sequential
import keras.layers
import chainer.links
import chainer.functions


class CKConvertChecker:
    def __init__(self, data_shape_nchw):
        self.data_shape_nchw = data_shape_nchw
        self.data_nchw = np.random.random(self.data_shape_nchw).astype(np.float32)
        self.c_link = None

    def run_chainer(self, link):
        self.c_link = link
        self.c_out = self.c_link(self.data_nchw).data

    def add_keras(self, layer):
        self.k_layer = layer
        self.k_model = Sequential()
        self.k_model.add(self.k_layer)

    def run_compare(self):
        self.k_model.compile(optimizer="sgd", loss="categorical_crossentropy")
        if self.data_nchw.ndim == 4:
            data_nhwc = np.transpose(self.data_nchw, (0, 2, 3, 1))
        else:
            data_nhwc = self.data_nchw
        k_out_nhwc = self.k_model.predict(data_nhwc)
        if k_out_nhwc.ndim == 4:
            k_out_nchw = np.transpose(k_out_nhwc, (0, 3, 1, 2))
        else:
            k_out_nchw = k_out_nhwc
        self.k_out = k_out_nchw

        try:
            assert np.allclose(self.c_out, self.k_out, rtol=1e-3, atol=1e-5)
        except AssertionError:
            print("c_out:", self.c_out)
            print("k_out:", self.k_out)
            raise


def main():
    checker = CKConvertChecker((2, 3))
    checker.run_chainer(chainer.links.Linear(in_size=3, out_size=2))
    checker.add_keras(keras.layers.Dense(units=2, input_dim=3))
    checker.k_layer.set_weights([checker.c_link.W.data.T, checker.c_link.b.data])
    checker.run_compare()

    checker = CKConvertChecker((2, 6, 5, 5))
    checker.run_chainer(chainer.links.Convolution2D(6, 4, ksize=3, stride=1, pad=1, initial_bias=1))
    checker.add_keras(
        keras.layers.Convolution2D(4, kernel_size=3, strides=1, padding="same", batch_input_shape=(2, 5, 5, 6)))
    # chainer kernel: (out, in, kh, kw)
    # keras kernel: (kh, kw, in, out)
    checker.k_layer.set_weights([checker.c_link.W.data.transpose((2, 3, 1, 0)), checker.c_link.b.data])
    checker.run_compare()

    checker = CKConvertChecker((2, 6, 5, 5))
    checker.run_chainer(chainer.links.Deconvolution2D(6, 4, ksize=3, stride=1, pad=1, initial_bias=1))
    checker.add_keras(keras.layers.Convolution2DTranspose(4, kernel_size=3, strides=1, padding="same",
                                                          batch_input_shape=(2, 5, 5, 6)))
    # chainer kernel: (out, in, kh, kw)
    # keras kernel: (kh, kw, in, out)
    checker.k_layer.set_weights([checker.c_link.W.data.transpose((2, 3, 1, 0)), checker.c_link.b.data])
    checker.run_compare()

    checker = CKConvertChecker((2, 6, 3, 3))
    # default epsilon in chainer is 2e-5
    c_bn = chainer.links.BatchNormalization(size=6, initial_gamma=np.random.rand(6).astype(np.float32),
                                            initial_beta=np.random.rand(6).astype(np.float32))
    c_bn.avg_mean = np.random.rand(6).astype(np.float32)
    c_bn.avg_var = np.random.rand(6).astype(np.float32)
    checker.run_chainer(c_bn)
    checker.add_keras(keras.layers.BatchNormalization(batch_input_shape=(2, 3, 3, 6), epsilon=2e-5))
    print(checker.k_layer.get_weights())
    checker.k_layer.set_weights([c_bn.gamma.data, c_bn.beta.data, c_bn.avg_mean, c_bn.avg_var])
    checker.run_compare()


if __name__ == "__main__":
    with chainer.using_config("train", False):
        main()
    print("OK")
