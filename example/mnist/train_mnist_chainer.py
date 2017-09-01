#!/usr/bin/env python

"""
WebDNN's example of training and converting mnist model to "graph descriptor"

Basic part is from example of Chainer (https://github.com/pfnet/chainer/)

Copyright (c) 2015 Preferred Infrastructure, Inc.
Copyright (c) 2015 Preferred Networks, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import print_function

try:
    import matplotlib

    matplotlib.use('Agg')
except ImportError:
    pass

import os
import argparse
import json

import numpy
import chainer
import chainer.functions as F
import chainer.links as L
from chainer import training
from chainer.training import extensions

from webdnn.backend import generate_descriptor
from webdnn.frontend.chainer import ChainerConverter


# Network definition
class MLP(chainer.Chain):
    """
    Simple multi-layer perceptron
    """

    def __init__(self, n_out):
        n_units = 100
        super().__init__(
            # the size of the inputs to each layer will be inferred
            l1=L.Linear(None, n_units),  # n_in -> n_units
            l2=L.Linear(None, n_units),  # n_units -> n_units
            l3=L.Linear(None, n_out),  # n_units -> n_out
        )

    def __call__(self, x):
        h1 = F.hard_sigmoid(self.l1(x))
        h2 = F.relu(self.l2(h1))
        return self.l3(h2)


class Conv(chainer.Chain):
    """
    Simple multi-layer perceptron
    """

    def __init__(self, n_out):
        super().__init__(
            # the size of the inputs to each layer will be inferred
            l1=L.Convolution2D(None, 8, ksize=3),  # n_in -> n_units
            l2=L.DilatedConvolution2D(None, 16, ksize=3, dilate=2),  # n_units -> n_units
            l3=L.Linear(None, n_out),  # n_units -> n_out
        )

    def __call__(self, x):
        h1 = F.sigmoid(self.l1(x))
        h2 = F.tanh(self.l2(h1))
        return self.l3(h2)


models = {"mlp": MLP, "conv": Conv}


def main():
    parser = argparse.ArgumentParser(description='Chainer example: MNIST')
    parser.add_argument("--model", default="mlp",
                        choices=["mlp", "conv"])
    parser.add_argument('--batchsize', '-b', type=int, default=100,
                        help='Number of images in each mini-batch')
    parser.add_argument('--epoch', '-e', type=int, default=5,
                        help='Number of sweeps over the dataset to train')
    parser.add_argument('--frequency', '-f', type=int, default=-1,
                        help='Frequency of taking a snapshot')
    parser.add_argument('--gpu', '-g', type=int, default=-1,
                        help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--out', '-o', default='output_chainer',
                        help='Directory to output the graph descriptor and sample test data')
    parser.add_argument('--resume', '-r', default='',
                        help='Resume the training from snapshot')
    args = parser.parse_args()

    print('GPU: {}'.format(args.gpu))
    print('# Minibatch-size: {}'.format(args.batchsize))
    print('# epoch: {}'.format(args.epoch))
    print('')

    os.makedirs(args.out, exist_ok=True)

    # Set up a neural network to train
    # Classifier reports softmax cross entropy loss and accuracy at every
    # iteration, which will be used by the PrintReport extension below.
    model = L.Classifier(models[args.model](10))
    if args.gpu >= 0:
        # Make a specified GPU current
        chainer.cuda.get_device_from_id(args.gpu).use()
        model.to_gpu()  # Copy the model to the GPU

    # Setup an optimizer
    optimizer = chainer.optimizers.Adam()
    optimizer.setup(model)

    # Load the MNIST dataset
    train, test = chainer.datasets.get_mnist(ndim=3)

    train_iter = chainer.iterators.SerialIterator(train, args.batchsize)
    test_iter = chainer.iterators.SerialIterator(test, args.batchsize,
                                                 repeat=False, shuffle=False)

    # Set up a trainer
    updater = training.StandardUpdater(train_iter, optimizer, device=args.gpu)
    trainer = training.Trainer(updater, (args.epoch, 'epoch'), out=os.path.join(args.out, 'chainer_model'))

    # Evaluate the model with the test dataset for each epoch
    trainer.extend(extensions.Evaluator(test_iter, model, device=args.gpu))

    # Dump a computational graph from 'loss' variable at the first iteration
    # The "main" refers to the target link of the "main" optimizer.
    trainer.extend(extensions.dump_graph('main/loss'))

    # Take a snapshot for each specified epoch
    frequency = args.epoch if args.frequency == -1 else max(1, args.frequency)
    trainer.extend(extensions.snapshot(), trigger=(frequency, 'epoch'))

    # Write a log of evaluation statistics for each epoch
    trainer.extend(extensions.LogReport())

    # Save two plot images to the result dir
    if extensions.PlotReport.available():
        trainer.extend(
            extensions.PlotReport(['main/loss', 'validation/main/loss'],
                                  'epoch', file_name='loss.png'))
        trainer.extend(
            extensions.PlotReport(
                ['main/accuracy', 'validation/main/accuracy'],
                'epoch', file_name='accuracy.png'))

    # Print selected entries of the log to stdout
    # Here "main" refers to the target link of the "main" optimizer again, and
    # "validation" refers to the default name of the Evaluator extension.
    # Entries other than 'epoch' are reported by the Classifier link, called by
    # either the updater or the evaluator.
    trainer.extend(extensions.PrintReport(
        ['epoch', 'main/loss', 'validation/main/loss',
         'main/accuracy', 'validation/main/accuracy', 'elapsed_time']))

    # Print a progress bar to stdout
    trainer.extend(extensions.ProgressBar())

    if args.resume:
        # Resume from a snapshot
        chainer.serializers.load_npz(args.resume, trainer)

    # Run the training
    trainer.run()

    # conversion
    print('Transpiling model to WebDNN graph descriptor')

    if args.gpu >= 0:
        model.to_cpu()
    example_input = numpy.expand_dims(train[0][0], axis=0)  # example input (anything ok, (batch_size, 784))
    x = chainer.Variable(example_input)
    # y = F.softmax(model.predictor(x))  # run model
    y = model.predictor(x)
    graph = ChainerConverter().convert([x], [y])  # convert graph to intermediate representation
    for backend in ["webgpu", "webgl", "webassembly", "fallback"]:
        exec_info = generate_descriptor(backend, graph)
        exec_info.save(args.out)

    print('Exporting test samples (for demo purpose)')
    test_samples_json = []
    for i in range(10):
        image, label = test[i]
        test_samples_json.append({'x': image.flatten().tolist(), 'y': int(label)})
    with open(os.path.join(args.out, 'test_samples.json'), 'w') as f:
        json.dump(test_samples_json, f)


if __name__ == '__main__':
    main()
