#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
converts chainer dataset to data matrices for webdnn

"""

import json
import numpy as np
import chainer
import matrix_serializer

def convert_sample(data_tuple):
    image, label = data_tuple
    return {'x': matrix_serializer.to_dict(image), 'y': int(label)}

def main():
    train, test = chainer.datasets.get_mnist()
    samples = []
    for i in range(10):
        samples.append(convert_sample(test[i]))
    with open("test_samples.json", "w") as f:
        json.dump(samples, f)

if __name__ == '__main__':
    main()
