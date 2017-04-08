#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
converts chainer model shapshot to weight matrices for webdnn

training of model in chainer 1.21
chainer/examples/mnist/train_mnist.py --unit 100
"""

import numpy as np
import matrix_serializer

def convert_fc_weight(buffers, weight_prefix, layer_name):
    w = buffers[weight_prefix + layer_name + "/W"]#(out_ch, in_ch)
    # transposition is needed (in_ch, out_ch)
    b = buffers[weight_prefix + layer_name + "/b"]#(out_ch, )
    return {layer_name + "/W": w.T, layer_name + "/b": b}

def main():
    snapshot_buffers = np.load("result_unit100/snapshot_iter_12000")
    weight_prefix = "updater/model:main/predictor/"
    weights = {}
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l1"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l2"))
    weights.update(convert_fc_weight(snapshot_buffers, weight_prefix, "l3"))
    matrix_serializer.save("mnist_weights.json", **weights)

if __name__ == '__main__':
    main()
