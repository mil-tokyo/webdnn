'''
This example is based on Keras's example.

Trains a LSTM on the IMDB sentiment classification task.
The dataset is actually too small for LSTM to be of any advantage
compared to simpler, much faster methods such as TF-IDF + LogReg.
Notes:

- RNNs are tricky. Choice of batch size is important,
choice of loss and optimizer is critical, etc.
Some configurations won't converge.

- LSTM loss decrease patterns during training can be quite different
from what you see with CNNs/MLPs/etc.
'''

import argparse
import json
import os
import subprocess
from os import path

from keras.datasets import imdb
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from keras.models import Sequential
from keras.preprocessing import sequence

max_features = 20000
maxlen = 80  # cut texts after this number of words (among top max_features most common words)
batch_size = 32
word_index_table = None


def word_index_to_sentence(idxs):
    global word_index_table
    if word_index_table is None:
        raw_index = imdb.get_word_index()  # {"the": 1, "and": 2, ...}
        word_index_table = {v + 3: k for k, v in raw_index.items()}  # {4: "the", 5: "and", ...}
        word_index_table[0] = ""  # padding
        word_index_table[1] = ""  # start of sentence
        word_index_table[2] = "_"  # out of vocabulary
        word_index_table[3] = ""  # ?
    return " ".join(map(lambda idx: word_index_table[idx], idxs))


def train_model(save_path, sample_output_path):
    print('Loading data...')
    (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=max_features)
    print(len(x_train), 'train sequences')
    print(len(x_test), 'test sequences')

    print('Pad sequences (samples x time)')
    x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
    x_test = sequence.pad_sequences(x_test, maxlen=maxlen)
    print('x_train shape:', x_train.shape)
    print('x_test shape:', x_test.shape)

    print('Build model...')
    model = Sequential()
    model.add(Embedding(max_features, 128))
    # model.add(ZeroPadding1D(padding=(0,1)))
    model.add(LSTM(64, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))  # stacked lstm
    model.add(LSTM(32, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(1, activation='sigmoid'))

    # try using different optimizers and different optimizer configs
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    print('Train...')
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=1,
              validation_data=(x_test, y_test))
    score, acc = model.evaluate(x_test, y_test,
                                batch_size=batch_size)
    print('Test score:', score)
    print('Test accuracy:', acc)

    model.save(save_path)

    print("Exporting test samples (for demo purpose)")
    export_size = 10
    x_export = x_test[:export_size]
    y_export = y_test[:export_size]
    orig_pred_export = model.predict(x_export, batch_size=batch_size)
    test_samples_json = []
    for i in range(export_size):
        word_index_list = x_export[i].tolist()
        text_sentence = word_index_to_sentence(word_index_list)
        test_samples_json.append({"x": word_index_list, "y": int(y_export[i]),
                                  "orig_pred": float(orig_pred_export[i, 0]), "orig_sentence": text_sentence})

    with open(sample_output_path, "w") as f:
        json.dump(test_samples_json, f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', '-o', default='output_keras',
                        help='Directory to output the graph descriptor')
    parser.add_argument("--encoding", help="name of weight encoder")

    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    original_model_path = path.join(args.out, "imdb_lstm.h5")
    if not path.exists(original_model_path):
        print("Training model")
        train_model(original_model_path, path.join(args.out, "imdb_lstm_samples.json"))
    else:
        print("Use already trained model")

    print("Converting model into WebDNN format (graph descriptor)")
    # only for demo purpose, maybe not safe
    convert_keras_command = f"python ../../bin/convert_keras.py {original_model_path} --input_shape '(1,{maxlen})' --out {args.out} --backend webgpu,webassembly"
    if args.encoding:
        convert_keras_command += f" --encoding {args.encoding}"
    print("$ " + convert_keras_command)

    subprocess.check_call(convert_keras_command, shell=True)

    print("Done.")


if __name__ == "__main__":
    main()
