# -*- coding:utf-8 -*-

"""
serialize matrices (array) into json
"""

import json
import numpy as np

def to_dict(array):
    shape = list(array.shape)
    data = array.flatten().tolist()
    return {"shape": shape, "data": data}

def save(f, **kwargs):
    if isinstance(f, str):
        with open(f, "w") as f_file:
            return save(f_file, **kwargs)
    mat_dict = {key: to_dict(value) for key, value in kwargs.items()}
    json.dump(mat_dict, f)

if __name__ == '__main__':
    pass
