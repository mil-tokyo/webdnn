"""
This example is based on keras's mnist_mlp.py and mnist_cnn.py

Trains a simple deep NN on the MNIST dataset.

Gets to 98.40% test accuracy after 20 epochs
(there is *a lot* of margin for parameter tuning).
2 seconds per epoch on a K520 GPU.
"""

from __future__ import print_function

import argparse
import os
import json

import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.optimizers import RMSprop
from keras import backend as K

parser = argparse.ArgumentParser()
parser.add_argument("--model", default="fc", choices=["fc", "conv"])
parser.add_argument("--out", default="output_mnist")
args = parser.parse_args()

batch_size = 128
num_classes = 10
epochs = 2

# the data, shuffled and split between train and test sets
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# input image dimensions
img_rows, img_cols = 28, 28

if args.model == "conv":
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
