"""
This example is based on keras's mnist_mlp.py and mnist_cnn.py

Trains a simple deep NN on the MNIST dataset.
"""

import argparse
import json
import os
import subprocess

batch_size = 128
num_classes = 10
epochs = 2
img_rows, img_cols = 28, 28


# noinspection PyPackageRequirements
def _get_input_shape(model_type):
    if model_type in ["conv", "dilated_conv", "residual", "complex"]:
        return img_rows, img_cols, 1

    elif model_type == "fc":
        return img_rows * img_cols,

    else:
        raise NotImplementedError("Unknown model type")


# noinspection PyPackageRequirements
def _setup_model(model_type):
    from keras import backend as K
    from keras.layers import Dense, Dropout, Flatten, Conv2D, AtrousConv2D, MaxPooling2D, Input, add, GlobalAveragePooling2D, Activation
    from keras.models import Sequential, Model

    input_shape = _get_input_shape(model_type)

    if model_type == "conv":
        model = Sequential()
        model.add(Conv2D(8, kernel_size=(3, 3), activation="relu", input_shape=input_shape))
        model.add(Conv2D(16, (3, 3), activation="relu"))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(32, activation="relu"))
        model.add(Dropout(0.5))
        model.add(Dense(num_classes, activation="softmax"))

    elif model_type == "dilated_conv":
        model = Sequential()
        model.add(AtrousConv2D(8, kernel_size=(3, 3), atrous_rate=(2, 2), activation="relu", input_shape=input_shape))  # shape is 5x5
        model.add(AtrousConv2D(16, kernel_size=(3, 3), atrous_rate=(3, 3), activation="relu"))  # shape is 7x7
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Flatten())
        model.add(Dense(32, activation="relu"))
        model.add(Dropout(0.5))
        model.add(Dense(num_classes, activation="softmax"))

    elif model_type == "fc":
        model = Sequential()
        model.add(Dense(512, activation="hard_sigmoid", input_shape=(784,)))
        model.add(Dropout(0.2))
        model.add(Dense(512, activation="relu"))
        model.add(Dropout(0.2))
        model.add(Dense(10, activation="softmax"))

    elif model_type == "residual":
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

    elif model_type == "complex":
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

    print(f"input shape: {input_shape}, data_format: {K.image_data_format()}")
    return model


# noinspection PyPackageRequirements
def train_and_save(model_type, model_path, sample_path):
    import keras
    from keras import backend as K
    from keras.datasets import mnist
    from keras.optimizers import RMSprop

    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    if model_type in ["conv", "dilated_conv", "residual", "complex"]:
        if K.image_data_format() == "channels_first":
            raise NotImplementedError("Currently, WebDNN converter does not data_format==channels_first")

        else:
            x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
            x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)

    elif model_type == "fc":
        x_train = x_train.reshape(x_train.shape[0], img_rows * img_cols)
        x_test = x_test.reshape(x_test.shape[0], img_rows * img_cols)

    else:
        raise NotImplementedError("Unknown model type")

    x_train = x_train.astype("float32")
    x_test = x_test.astype("float32")
    x_train /= 255
    x_test /= 255
    print(x_train.shape[0], "train_and_save samples")
    print(x_test.shape[0], "test samples")

    # convert class vectors to binary class matrices
    y_test_orig = y_test  # for exporting test sample
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)

    model = _setup_model(model_type)
    model.summary()
    model.compile(loss="categorical_crossentropy", optimizer=RMSprop(), metrics=["accuracy"])
    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1, validation_data=(x_test, y_test))

    score = model.evaluate(x_test, y_test, verbose=0)
    print("Test loss:", score[0])
    print("Test accuracy:", score[1])

    print("Saving trained model")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)

    print("Exporting test samples (for demo purpose)")
    test_samples_json = []
    for i in range(10):
        test_samples_json.append({"x": x_test[i].flatten().tolist(), "y": int(y_test_orig[i])})

    with open(sample_path, "w") as f:
        json.dump(test_samples_json, f)


def convert(backend, model_path, input_shape, out_path):
    print("Converting model into WebDNN format (graph descriptor)")

    input_shape_with_batchsize = ('1',) + input_shape

    # only for demo purpose, maybe not safe
    convert_keras_command = f"python ../../bin/convert_keras.py {model_path} " \
                            f"--backend {backend} " \
                            f"--input_shape '{input_shape_with_batchsize}' " \
                            f"--out {out_path}"
    print("$ " + convert_keras_command)
    subprocess.check_call(convert_keras_command, shell=True)

    print("Done.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="fc", choices=["fc", "conv", "dilated_conv", "residual", "complex"])
    parser.add_argument("--out", default="output_keras")
    parser.add_argument("--backend", default="webgpu,webgl,webassembly,fallback")
    args = parser.parse_args()

    model_path = os.path.join(args.out, f"./keras_model/{args.model}.h5")
    sample_path = os.path.join(args.out, "test_samples.json")

    if not os.path.exists(model_path):
        train_and_save(args.model, model_path, sample_path)

    convert(args.backend, model_path, _get_input_shape(args.model), args.out)


if __name__ == "__main__":
    main()
