import numpy as np
from typing import Dict


class KBChannelwiseWeightOperator:
    """
    Channelwiseかつ1つのウェイトをとる処理
    """

    def __init__(self, func_name: str, sources: Dict[str, str], serial_generator, param_offset: int):
        self.func_name = func_name
        self.sources = sources
        self.serial_generator = serial_generator
        self._param_data_name = "param_data" + str(self.serial_generator.get())
        # meta_bufferのポインタを進め、self.meta_bufferの内容を読み取る
        self.post_init_source = """
const device float *{0} = param_buffer + (*meta_buffer++);
        """.format(self._param_data_name)
        self.meta_buffer = np.array([param_offset], dtype=np.int32).tobytes()

    def wrap_expression(self, expression: str):
        return "{0}({1}, {2}[out_chid])".format(self.func_name, expression, self._param_data_name)
