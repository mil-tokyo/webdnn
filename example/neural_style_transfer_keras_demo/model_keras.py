import numpy as np

from keras import backend as K
from keras.layers import BatchNormalization, Deconvolution2D, Convolution2D, Input, Activation, add
from keras.models import Model


class WeightConverter:
    def __init__(self):
        self.layers = {}  # name, layer

    def add(self, name, layer):
        self.layers[name] = layer
        return layer


    def assign(self, weight_dict):
        for name, layer in self.layers.items():
            try:
                if isinstance(layer, (Convolution2D, Deconvolution2D)):
                    w = weight_dict[name+"/W"]
                    b = weight_dict[name+"/b"]
                    layer.set_weights([w.transpose((2,3,1,0)), b])
                elif isinstance(layer, BatchNormalization):
                    layer.set_weights([
                        weight_dict[name+"/gamma"],
                        weight_dict[name+"/beta"],
                        weight_dict[name+"/avg_mean"],
                        np.maximum(weight_dict[name+"/avg_var"], 1e-2)
                    ])
                    print(weight_dict[name+"/avg_var"])
                else:
                    raise NotImplementedError
            except:
                print("Error on " + name)
                raise


def create_model(wc: WeightConverter, h):
    h = wc.add("c1", Convolution2D(32, kernel_size=9, strides=1, padding="same"))(h)
    h = Activation("elu")(h)
    h = wc.add("b1", BatchNormalization(epsilon=2e-5))(h)
    h = wc.add("c2", Convolution2D(64, kernel_size=4, strides=2, padding="same"))(h)
    h = Activation("elu")(h)
    h = wc.add("b2", BatchNormalization(epsilon=2e-5))(h)
    h = wc.add("c3", Convolution2D(128, kernel_size=4, strides=2, padding="same"))(h)
    h = Activation("elu")(h)
    h = wc.add("b3", BatchNormalization(epsilon=2e-5))(h)
    h = residual_block(wc, 128, 128, h, "r1/")
    h = residual_block(wc, 128, 128, h, "r2/")
    h = residual_block(wc, 128, 128, h, "r3/")
    h = residual_block(wc, 128, 128, h, "r4/")
    h = residual_block(wc, 128, 128, h, "r5/")
    h = wc.add("d1", Deconvolution2D(64, kernel_size=4, strides=2, padding="same"))(h)
    h = Activation("elu")(h)
    h = wc.add("b4", BatchNormalization(epsilon=2e-5))(h)
    h = wc.add("d2", Deconvolution2D(32, kernel_size=4, strides=2, padding="same"))(h)
    h = Activation("elu")(h)
    h = wc.add("b5", BatchNormalization(epsilon=2e-5))(h)
    h = wc.add("d3", Deconvolution2D(3, kernel_size=9, strides=1, padding="same"))(h)
    h = Activation("tanh")(h)
    # h = (h + 1) * 127.5
    return h


def residual_block(wc: WeightConverter, n_in, n_out, h, prefix):
    x = h
    l = Convolution2D(n_out, kernel_size=3, strides=1, padding="same")
    wc.add(prefix + "c1", l)
    h = l(h)
    l = BatchNormalization(epsilon=2e-5)
    wc.add(prefix + "b1", l)
    h = l(h)
    h = Activation("relu")(h)
    l = Convolution2D(n_out, kernel_size=3, strides=1, padding="same")
    wc.add(prefix + "c2", l)
    h = l(h)
    l = BatchNormalization(epsilon=2e-5)
    wc.add(prefix + "b2", l)
    h = l(h)
    return add([h, x])

def main():
    wc = WeightConverter()
    nn_input = Input(shape=(144, 192, 3))
    nn_output = create_model(wc, nn_input)
    model = Model(inputs=[nn_input], outputs=[nn_output])
    model.compile(optimizer="sgd", loss="categorical_crossentropy")
    #weight_dict = np.load("../../resources/chainer-fast-neuralstyle-models/models/kanagawa.model")
    weight_dict = np.load("../../resources/chainer-fast-neuralstyle-models/models/candy_512_2_49000.model")
    wc.assign(weight_dict)
    model.save("keras_cc.h5")

main()
