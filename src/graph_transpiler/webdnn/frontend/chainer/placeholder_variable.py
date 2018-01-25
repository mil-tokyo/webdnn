from typing import Sequence, Tuple, Union

import chainer
import numpy as np

from webdnn.graph.placeholder import Placeholder

DEFAULT_SIZE = 128


# noinspection PyAbstractClass
class PlaceholderVariable(chainer.Variable):
    def __init__(self, shape: Sequence[Union[int, Placeholder]], dummy_shape: Sequence[int] = None):
        for v in shape:
            if isinstance(v, (int, Placeholder)):
                continue

            else:
                raise TypeError("[PlaceholderVariable] Each element in parameter \"shape\" must be int or placeholder")

        if dummy_shape is None:
            dummy_shape = tuple(v if isinstance(v, int) else DEFAULT_SIZE for v in shape)

        else:
            assert len(shape) == len(dummy_shape), "[PlaceholderVariable] Length of parameter \"shape\" and \"dummy_shape\" must be same"

        self._webdnn_dummy_shape = tuple(dummy_shape)  # type: Tuple[int, ...]
        self._webdnn_actual_shape = tuple(shape)  # type: Tuple[Union[int, Placeholder], ...]
        dummy_value = np.zeros(self._webdnn_dummy_shape, dtype=np.float32)
        super(PlaceholderVariable, self).__init__(data=dummy_value)

    @property
    def actual_shape(self):
        return self._webdnn_actual_shape
