# Using LSTM model

LSTM is a DNN layer which accepts sequence and update internal state according to it. LSTM is widely used for natual lauguage analysis and generation. If you are new to LSTM itself, refer to [articles](http://karpathy.github.io/2015/05/21/rnn-effectiveness/) of sequential models.

From WebDNN 1.1.0, LSTM layer is supported. As of WebDNN 1.1.0, automatic model conversion is supported only from Keras. Compared to image classification model, using LSTM-based model requires more implementation in JavaScript side. This document describes some common use-cases of LSTM.

## Sequence input, final state output
`example/lstm` illustrates the most simple usage of LSTM model. The model accepts sequence of words in sentences, and outputs its sentiment as a scalar value (vector with only 1 elements).

The simplest model definition is as follows.
```python
model = Sequential()
model.add(Embedding(max_features, 128))
model.add(LSTM(32, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(1, activation='sigmoid'))
```

Also, you can stack LSTM for higher model accuracy. First LSTM layer now outputs sequence of states, not only last state. But this modification does not affect input/output format of the whole model.

```python
model = Sequential()
model.add(Embedding(max_features, 128))
model.add(LSTM(64, dropout=0.2, recurrent_dropout=0.2, return_sequences=True))  # stacked lstm
model.add(LSTM(32, dropout=0.2, recurrent_dropout=0.2))
model.add(Dense(1, activation='sigmoid'))
```

Usage of this model in descriptor runner is the same as image classification CNN model.

```javascript
runner.getInputViews()[0].set(input_sequence);
await runner.run();
let prediction_vector = runner.getOutputViews()[0].toActual();
```

## Iterative sequence generation
Natural language generation models generally requires iterative execution of LSTM model with sampling.

One kind of such models accept last N characters (or words) of the sentence and predicts probability of next character (or word). Then, concrete character is selected according to the probability (select character with highest probability or randomly sampling with predicted probability). This selection is called as sampling. Then, selected character is concatenated to the sentence. By iteratively executing such procedures, long sentences are generated.

`example/text_generation` is the example of sentence generation using the procedure mentioned above. The model definition is follows:

```python
model = Sequential()
model.add(LSTM(128, input_shape=(maxlen, len(chars))))
model.add(Dense(len(chars)))
model.add(Activation('softmax'))
```

The model accepts last `maxlen` characters of the sentence, and outputs next character's probability. WebDNN itself does not support character sampling, so it have to be implemented in JavaScript. By feeding updated sentence to descriptor runner iteratively, a sentence is generated.

```javascript
let sentence = sentence_seed;

for (let i = 0; i < 100; i++) {
    // input current sentence to the model
    runner.getInputViews()[0].set(sentence_to_array(sentence));

    // predict next character's probability
    await runner.run();
    let out_vec = runner.getOutputViews()[0].toActual();
    // sample next character
    let next_char = sample_next_char(out_vec, 1.0);
    sentence += next_char;
}
```

Function `sentence_to_array` generates sequence of one-hot-vector of last `maxlen` characters. Function `sample_next_char` samples concrete character from probability vector from the model.

## More advanced example
One of the more advanced examples is image captioning. Image captioning is an application that generate natural language sentence which describes given image.

[https://github.com/milhidaka/chainer-image-caption](https://github.com/milhidaka/chainer-image-caption)

In this example, the following techniques are used:
- Converting Chainer model manually into WebDNN IR
- Using multiple descriptor runner (image feature extraction and sentence generation)
- Switching two inputs in sentence generation
  - LSTM requires image feature for first iteration, then requires sampled character

This example is a reference for using complex model in WebDNN.
