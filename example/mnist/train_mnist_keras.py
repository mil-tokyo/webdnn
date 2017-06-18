"""
This example is based on keras's mnist_mlp.py and mnist_cnn.py

Trains a simple deep NN on the MNIST dataset.
"""

from __future__ import print_function

import argparse
import os
import json
import subprocess

import keras
from keras.datasets import mnist
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, Input, add, GlobalAveragePooling2D, Activation
from keras.optimizers import RMSprop
from keras import backend as K

parser = argparse.ArgumentParser()
parser.add_argument("--model", default="fc", choices=["fc", "conv", "residual", "complex"])
parser.add_argument("--out", default="output_keras")
args = parser.parse_args()

batch_size = 128
num_classes = 10
epochs = 2

# the data, shuffled and split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# input image dimensions
img_rows, img_cols = 28, 28

if args.model in ["conv", "residual", "complex"]:
    if K.image_data_format() == "channels_first":
        raise NotImplementedError("Currently, WebDNN converter does not data_format==channels_first")
        # x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        # x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        # input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)
elif args.model == "fc":
    x_train = x_train.reshape(x_train.shape[0], img_rows * img_cols)
    x_test = x_test.reshape(x_test.shape[0], img_rows * img_cols)
    input_shape = (img_rows * img_cols,)
else:
    raise NotImplementedError("Unknown model type")

print(f"input shape: {input_shape}, data_format: {K.image_data_format()}")
x_train = x_train.astype("float32")
x_test = x_test.astype("float32")
x_train /= 255
x_test /= 255
print(x_train.shape[0], "train samples")
print(x_test.shape[0], "test samples")

# convert class vectors to binary class matrices
y_test_orig = y_test  # for exporting test sample
y_train = keras.utils.to_categorical(y_train, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

if args.model == "conv":
    model = Sequential()
    model.add(Conv2D(8, kernel_size=(3, 3),
                     activation="relu",
                     input_shape=input_shape))
    model.add(Conv2D(16, (3, 3), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())
    model.add(Dense(32, activation="relu"))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation="softmax"))
elif args.model == "fc":
    model = Sequential()
    model.add(Dense(512, activation="relu", input_shape=(784,)))
    model.add(Dropout(0.2))
    model.add(Dense(512, activation="relu"))
    model.add(Dropout(0.2))
    model.add(Dense(10, activation="softmax"))
elif args.model == "residual":
    nn_input = Input(shape=(28, 28, 1))
    hidden = Conv2D(8, kernel_size=(3, 3), activation="relu")(nn_input)
    hidden = MaxPooling2D(pool_size=(2, 2))(hidden)
    hidden_1 = Conv2D(16, kernel_size=(1, 1), activation="relu", padding="same")(hidden)
    hidden_2 = Conv2D(16, kernel_size=(3, 3), activation="relu", padding="same")(hidden)
    hidden = add([hidden_1, hidden_2])
    hidden_1 = hidden
    hidden_2 = Conv2D(16, kernel_size=(3, 3), activation="relu", padding="same")(hidden)
    hidden = add([hidden_1, hidden_2])
    hidden = GlobalAveragePooling2D()(hidden)
    nn_output = Dense(num_classes, activation="softmax")(hidden)

    model = Model(inputs=[nn_input], outputs=[nn_output])
elif args.model == "complex":
    # graph which has graph and sequential
    # this is for testing converting complex model
    nn_input = Input(shape=(28, 28, 1))

    hidden_1 = Conv2D(8, kernel_size=(3, 3), activation="relu")(nn_input)

    submodel_input = Input(shape=(26, 26, 8))
    submodel_conv = Conv2D(8, kernel_size=(3, 3), activation="relu")
    submodel_1 = submodel_conv(submodel_input)
    submodel_2 = submodel_conv(submodel_1)  # use same layer multiple times
    submodel_3 = Conv2D(16, kernel_size=(3, 3), activation="relu")(submodel_1)
    submodel = Model(inputs=[submodel_input], outputs=[submodel_3, submodel_2])

    subseq = Sequential()
    subseq.add(Conv2D(16, kernel_size=(3, 3), activation="relu", input_shape=(22, 22, 16)))
    subseq.add(Flatten())
    subseq.add(Dense(10))

    hidden_2, hidden_3 = submodel(hidden_1)
    hidden_4 = subseq(hidden_2)
    hidden_5 = Flatten()(hidden_3)
    hidden_6 = Dense(10)(hidden_5)
    hidden_sum = add([hidden_4, hidden_6])
    nn_output = Activation(activation="softmax")(hidden_sum)

    model = Model(inputs=[nn_input], outputs=[nn_output])

else:
    raise NotImplementedError("Unknown model type")

model.summary()

model.compile(loss="categorical_crossentropy",
              optimizer=RMSprop(),
              metrics=["accuracy"])

history = model.fit(x_train, y_train,
                    batch_size=batch_size,
                    epochs=epochs,
                    verbose=1,
                    validation_data=(x_test, y_test))
score = model.evaluate(x_test, y_test, verbose=0)
print("Test loss:", score[0])
print("Test accuracy:", score[1])

print("Saving trained model")
os.makedirs(os.path.join(args.out, "keras_model"), exist_ok=True)
model.save(os.path.join(args.out, "keras_model/mnist_mlp.h5"))

print("Exporting test samples (for demo purpose)")
test_samples_json = []
for i in range(10):
    test_samples_json.append({"x": x_test[i].flatten().tolist(), "y": int(y_test_orig[i])})
with open(os.path.join(args.out, "test_samples.json"), "w") as f:
    json.dump(test_samples_json, f)

print("Converting model into WebDNN format (graph descriptor)")
input_shape_with_batchsize = (1,) + input_shape
# only for demo purpose, maybe not safe
convert_keras_command = f"python ../../bin/convert_keras.py {args.out}/keras_model/mnist_mlp.h5 --input_shape '{input_shape_with_batchsize}' --out {args.out}"
print("$ " + convert_keras_command)

subprocess.check_call(convert_keras_command, shell=True)

print("Done.")
