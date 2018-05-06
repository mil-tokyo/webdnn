# algorithm, implementation is based on "8-Bit Approximations for Parallelism in Deep Learning" by Tim Dettmers
# https://github.com/TimDettmers/clusterNet/blob/master/source/clusterKernels.cu

import zlib

import numpy as np

from webdnn.backend.code_generator.allocator import Allocation, MemoryLayout
from webdnn.encoder.constant_encoder import ConstantEncoder

tbl_floats = [2.750000021e-06, 7.249999726e-06, 1.875000089e-05, 3.624999954e-05, 5.874999624e-05, 8.624999464e-05,
              1.437500032e-04, 2.312500001e-04, 3.187500115e-04, 4.062500084e-04, 5.187499919e-04, 6.562499912e-04,
              7.937499322e-04, 9.312499315e-04, 1.218750025e-03, 1.656249980e-03, 2.093750052e-03, 2.531250007e-03,
              2.968749963e-03, 3.406249918e-03, 3.843750106e-03, 4.281249829e-03, 4.843750037e-03, 5.531250034e-03,
              6.218749564e-03, 6.906249560e-03, 7.593749557e-03, 8.281249553e-03, 8.968749084e-03, 9.656248614e-03,
              1.109374966e-02, 1.328125037e-02, 1.546875015e-02, 1.765624993e-02, 1.984374970e-02, 2.203124948e-02,
              2.421874925e-02, 2.640625089e-02, 2.859375067e-02, 3.078125045e-02, 3.296874836e-02, 3.515625000e-02,
              3.734375164e-02, 3.953124955e-02, 4.171875119e-02, 4.390624911e-02, 4.671875015e-02, 5.015625060e-02,
              5.359374732e-02, 5.703124776e-02, 6.046874821e-02, 6.390624493e-02, 6.734374911e-02, 7.078124583e-02,
              7.421874255e-02, 7.765624672e-02, 8.109374344e-02, 8.453124017e-02, 8.796874434e-02, 9.140624106e-02,
              9.484373778e-02, 9.828124195e-02, 1.054687500e-01, 1.164062470e-01, 1.273437440e-01, 1.382812560e-01,
              1.492187530e-01, 1.601562500e-01, 1.710937470e-01, 1.820312440e-01, 1.929687560e-01, 2.039062530e-01,
              2.148437500e-01, 2.257812470e-01, 2.367187440e-01, 2.476562560e-01, 2.585937381e-01, 2.695312500e-01,
              2.804687619e-01, 2.914062440e-01, 3.023437560e-01, 3.132812381e-01, 3.242187500e-01, 3.351562619e-01,
              3.460937440e-01, 3.570312560e-01, 3.679687381e-01, 3.789062500e-01, 3.898437619e-01, 4.007812440e-01,
              4.117187560e-01, 4.226562381e-01, 4.335937500e-01, 4.445312619e-01, 4.585937560e-01, 4.757812321e-01,
              4.929687381e-01, 5.101562142e-01, 5.273437500e-01, 5.445312262e-01, 5.617187023e-01, 5.789062381e-01,
              5.960937142e-01, 6.132812500e-01, 6.304687262e-01, 6.476562023e-01, 6.648437381e-01, 6.820312142e-01,
              6.992186904e-01, 7.164062262e-01, 7.335937023e-01, 7.507811785e-01, 7.679687142e-01, 7.851561904e-01,
              8.023436666e-01, 8.195312023e-01, 8.367186785e-01, 8.539061546e-01, 8.710936904e-01, 8.882811666e-01,
              9.054686427e-01, 9.226561785e-01, 9.398436546e-01, 9.570311308e-01, 9.742186666e-01, 9.914061427e-01]

thres_low = 1.5e-6
thres_high = 0.995703

# symbol 0 => 0.0
# symbol 1 => 2.75e-6
# symbol 2 => 7.24e-6
# symbol 126 => 9.91e-6
# symbol 127 => 1.0

# thresholds: [1.5e-6, (2.75e-6+7.24e-6)/2, ..., (9.74e-1+9.91e-1)/2, 9.95e-1] (len=127)

thresholds = []
for i in range(127):
    if i == 0:
        thresholds.append(thres_low)
    elif i < 126:
        thresholds.append((tbl_floats[i] + tbl_floats[i - 1]) / 2.0)
    else:
        thresholds.append(thres_high)
threshold_array = np.array(thresholds, dtype=np.float32)


class ConstantEncoderEightbit(ConstantEncoder):
    def __init__(self):
        self.name = "eightbit"

    def encode(self, memory_layout: MemoryLayout) -> bytes:
        all_code = b""
        for alloc in memory_layout.allocations.values():
            # TODO
            # This if-statement checks whether this allocation has the initial values.
            #
            # We should improve this as follows:
            #   1. Instead of concatenating all initial values, separate them and store it in each allocation instance.
            #   2. When generating graph descriptor and related assets, concatenate them.
            #
            if alloc.offset < 0 or alloc.offset >= memory_layout.data.size:
                continue

            single_data = memory_layout.data[alloc.offset:alloc.offset + alloc.size]
            all_code += self._single_encode(single_data, alloc)

        return all_code

    # noinspection PyMethodMayBeStatic
    def _single_encode(self, single_data: np.ndarray, alloc: Allocation) -> bytes:
        maxval = np.max(np.abs(single_data))
        maxval = np.maximum(maxval, 1e-20)  # avoid zero division
        abs_scaled_data = np.abs(single_data) / maxval
        code = np.searchsorted(threshold_array, abs_scaled_data)
        code += (single_data < 0.0).astype(np.int32) * 128
        code_raw_bytes = code.astype(np.uint8).tobytes("C")
        code_bytes = zlib.compress(code_raw_bytes, level=9)

        out_data = b""
        out_data += np.array([alloc.offset, len(code_bytes)], dtype=np.int32).tobytes()
        out_data += np.array([maxval], dtype=np.float32).tobytes()
        out_data += np.array([0], dtype=np.int32).tobytes()
        out_data += code_bytes

        return out_data
