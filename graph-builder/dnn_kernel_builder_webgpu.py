# -*- coding:utf-8 -*-

"""
DNN Kernel Builder for WebGPU

- kernel source generation
- schedule memory allocation
"""

from enum import Enum, auto
from collections import defaultdict, OrderedDict
from typing import List, Set, Dict, Tuple
import numpy as np
from dnn_graph import DNNLayer, DNNLayerAttributes, DNNLayerType, DNNVariable, DNNGraphNode, DNNGraph

next_unique_suffix_number = 0


def get_unique_suffix():
    global next_unique_suffix_number
    suffix = '_u{}'.format(next_unique_suffix_number)
    next_unique_suffix_number += 1
    return suffix


SIZEOF_FLOAT = 4


class DNNDescriptor:
    pass


class DNNKernelBuilder:
    pass


class DNNDescriptorWebGPU(DNNDescriptor):
    def __init__(self):
        pass


base_kernel = """
#include <metal_stdlib>
using namespace metal;


"""


class DNNKernelBuilderWebGPU(DNNKernelBuilder):
    def __init__(self, graph: DNNGraph):
        self.graph = graph
        self.weight_array = None
        self.description = None

    def build(self):
        weights = self._enum_weights()
        weight_allocation = self._allocate_weights(weights)
        self.weight_array = self._gather_weights(weights, weight_allocation)
        variables = self._enum_variables()
        variable_allocation = self._allocate_variables(variables)
        kernels = self._get_layers_kernels(weight_allocation, variable_allocation)
        self.description = self._make_description(kernels, weight_allocation, variable_allocation)

    def _enum_weights(self):
        """
        ウェイト一覧を作成する
        """
        weights = {}  # (layer_name, weight_name) => array
        for node in self.graph.nodes:
            for layer in node.layer.iterate_self_and_children():
                layer_name = layer.name
                for weight_name, array in layer.weights.items():
                    weights[(layer_name, weight_name)] = array
        return weights

    def _allocate_weights(self, weights):
        """
        ウェイトの割付アドレスを決める
        """
        offset = 0
        weight_allocation = {}
        for weight_id, array in weights.items():
            size = array.size
            weight_name = '/'.join(weight_id)
            weight_allocation[weight_name] = KBAllocatedWeight(weight_name, offset, size)
            offset += size
        total_size = offset
        return KBWeightAllocation(total_size, weight_allocation)

    def _gather_weights(self, weights, weight_allocation):
        dst_buf = np.zeros((weight_allocation.total_size), dtype=np.float32)
        for weight_id, array in weights.items():
            weight_name = '/'.join(weight_id)
            al_info = weight_allocation.allocation[weight_name]
            dst_buf[al_info.offset:al_info.offset + al_info.size] = array.flatten()
        return dst_buf

    def _enum_variables(self):
        variables = {}  # name => DNNVariable
        for node in self.graph.nodes:
            for v in node.bottoms + node.tops:
                variables[v.name] = v
                # TODO: temporary variable (im2colのバッファなど、サイズが実装依存なのでbuilder内でサイズを決めて確保)
        return variables

    def _allocate_variables(self, variables):
        """
        変数の割付アドレスを決める
        """
        offset = 0
        variable_allocation = {}
        for name, array in variables.items():
            size = int(np.prod(array.shape))
            variable_allocation[name] = KBAllocatedVariable(name, offset, size)
            offset += size
        total_size = offset
        return KBVariableAllocation(total_size, variable_allocation)

    def _get_layers_kernels(self, weight_allocation, variable_allocation):
        all_kernels = []
        for node in self.graph.nodes:
            layer = node.layer
            kb_layer = KBLayerGenerator.generate(layer)
            kernels = kb_layer.generate_kernels(self.graph.batch_size, node.bottoms, node.tops, weight_allocation,
                                                variable_allocation)
            all_kernels.extend(kernels)
        return all_kernels

    def _combine_kernel_source(self, kernels):
        sources = OrderedDict()  # to preserve function order
        sources[''] = base_kernel
        for kernel in kernels:
            # functions of same name appears once
            for func_name, source in kernel.func_sources.items():
                if func_name in sources:
                    assert sources[func_name] == source
                else:
                    sources[func_name] = source
        combined_source = '\n'.join(sources.values())
        return combined_source

    def _make_execution_info(self, kernel):
        d = {}
        d['entry_func_name'] = kernel.entry_func_name
        d['threadgroups_per_grid'] = kernel.threadgroups_per_grid
        d['threads_per_thread_group'] = kernel.threads_per_thread_group
        # [1, 0, 0, 0, ...]
        d['meta_buffer'] = np.fromstring(kernel.meta_buffer, dtype=np.uint8).tolist()
        return d

    def _make_description(self, kernels, weight_allocation, variable_allocation):
        kernel_source = self._combine_kernel_source(kernels)
        exec_infos = list(map(self._make_execution_info, kernels))
        return {'kernel_source': kernel_source, 'exec_infos': exec_infos,
                'weight_allocation': weight_allocation.to_dict(),
                'variable_allocation': variable_allocation.to_dict(),
                'inputs': [v.name for v in self.graph.inputs],
                'outputs': [v.name for v in self.graph.outputs],
                'batch_size': self.graph.batch_size
                }


class KBAllocatedVariable:
    def __init__(self, name: str, offset: int, size: int):
        # unit = SIZEOF_FLOAT
        self.name = name
        self.offset = offset
        self.size = size

    def to_dict(self):
        return {'name': self.name, 'offset': self.offset, 'size': self.size}


class KBVariableAllocation:
    def __init__(self, total_size: int, allocation: Dict[str, KBAllocatedVariable]):
        self.total_size = total_size
        self.allocation = allocation

    def to_dict(self):
        return {'total_size': self.total_size, 'allocation': {k: v.to_dict() for k, v in self.allocation.items()}}


class KBAllocatedWeight:
    def __init__(self, name: str, offset: int, size: int):
        # unit = SIZEOF_FLOAT
        self.name = name
        self.offset = offset
        self.size = size

    def to_dict(self):
        return {'name': self.name, 'offset': self.offset, 'size': self.size}


class KBWeightAllocation:
    def __init__(self, total_size: int, allocation: Dict[str, KBAllocatedWeight]):
        self.total_size = total_size
        self.allocation = allocation

    def to_dict(self):
        return {'total_size': self.total_size, 'allocation': {k: v.to_dict() for k, v in self.allocation.items()}}


class KernelData:
    def __init__(self, func_sources: Dict[str, str], entry_func_name: str, threadgroups_per_grid,
                 threads_per_thread_group, meta_buffer: bytes):
        self.func_sources = func_sources
        self.entry_func_name = entry_func_name
        self.threadgroups_per_grid = threadgroups_per_grid
        self.threads_per_thread_group = threads_per_thread_group
        self.meta_buffer = meta_buffer


class KBLayerAttribute(Enum):
    Elementwise = auto()
    Channelwise = auto()


class KBLayer:
    def __init__(self, layer: DNNLayer, name: str, attributes: Set[KBLayerAttribute]):
        self.layer = layer
        self.name = name
        self.attributes = attributes

    def generate_kernels(self, batch_size: int,
                         bottoms: List[DNNVariable], tops: List[DNNVariable],
                         weight_allocation: KBWeightAllocation, variable_allocation: KBVariableAllocation) -> List[
        KernelData]:
        pass


linear_mul_source = """
kernel void %%FUNC_NAME%%(const device float *weight_buffer[[buffer(0)]],
                 device float *data_buffer[[buffer(1)]],
                 const device int *meta_buffer[[buffer(2)]],
                  uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + (*meta_buffer++);
  device float *output_data = data_buffer + (*meta_buffer++);
  const device float *weight_data = weight_buffer + (*meta_buffer++);
  const int n = (*meta_buffer++);
  const int out_ch = (*meta_buffer++);
  const int in_ch = (*meta_buffer++);
  %%POST_INIT%%
    for (int gid = index; gid < n; gid += 4096) {
      int out_chid = gid % out_ch;
      int sample_id = gid / out_ch;
      float sum = 0.0;
      for (int in_chid = 0; in_chid < in_ch; in_chid++) {
        sum += input_data[sample_id * in_ch + in_chid] * weight_data[in_chid * out_ch + out_chid];
      }
      output_data[gid] = %%MAKE_OUTPUT%%;
    }
}
"""

elementwise_relu_source = """
float elementwise_relu(float x)
{
    return x >= 0.0 ? x : 0.0;
}
"""

channelwise_bias_source = """
float channelwise_bias(float x, float weight)
{
    return x + weight;
}
"""


class KBKernelSerialGenerator():
    """
    1カーネル内でユニークな変数suffixを作るためのカウンタ
    カーネル内だけでシリアルを作ることで、同じ組み合わせ(linear-bias)で同じカーネルソースになることを期待している
    """

    def __init__(self):
        self.value = 0

    def get(self):
        value = self.value
        self.value += 1
        return value


class KBLinearLayer(KBLayer):
    def __init__(self, layer: DNNLayer):
        super().__init__(layer, 'linear', set())

    def generate_kernels(self, batch_size: int,
                         bottoms: List[DNNVariable], tops: List[DNNVariable],
                         weight_allocation: KBWeightAllocation, variable_allocation: KBVariableAllocation) -> List[
        KernelData]:
        layer = self.layer
        n = layer.parameters['out_size'] * batch_size
        bottom_av = variable_allocation.allocation[bottoms[0].name]
        top_av = variable_allocation.allocation[tops[0].name]
        weight_aw = weight_allocation.allocation[self.layer.name + '/W']
        meta_array = np.array([bottom_av.offset, top_av.offset, weight_aw.offset, n, layer.parameters['out_size'],
                               layer.parameters['in_size']], dtype=np.int32)
        meta_buffer = meta_array.tobytes()
        threadgroups_per_grid = {'width': 8, 'height': 1, 'depth': 1}
        threads_per_thread_group = {'width': 512, 'height': 1, 'depth': 1}
        sources = OrderedDict()  # to preserve order
        func_name = 'linear_mul_'
        make_output = 'sum'
        post_init_source = ''
        serial_generator = KBKernelSerialGenerator()
        for child in self.layer.iterate_self_and_children():
            if child.is_root:
                continue
            kb_child_layer = KBLayerGenerator.generate(child)
            if KBLayerAttribute.Elementwise in kb_child_layer.attributes:
                elementwise_operator = kb_child_layer.get_elementwise_operator(weight_allocation, serial_generator)
                post_init_source += elementwise_operator.post_init_source
                make_output = elementwise_operator.wrap_expression(make_output)
                func_name += kb_child_layer.name + '_'
                sources.update(elementwise_operator.sources)
                meta_buffer += elementwise_operator.meta_buffer
            elif KBLayerAttribute.Channelwise in kb_child_layer.attributes:
                channelwise_operator = kb_child_layer.get_channelwise_operator(weight_allocation, serial_generator)
                post_init_source += channelwise_operator.post_init_source
                make_output = channelwise_operator.wrap_expression(make_output)
                func_name += kb_child_layer.name + '_'
                sources.update(channelwise_operator.sources)
                meta_buffer += channelwise_operator.meta_buffer
            else:
                raise NotImplementedError()
        sources[func_name] = linear_mul_source.replace('%%POST_INIT%%', post_init_source) \
            .replace('%%FUNC_NAME%%', func_name) \
            .replace('%%MAKE_OUTPUT%%', make_output)

        kernel_data = KernelData(sources, func_name, threadgroups_per_grid, threads_per_thread_group, meta_buffer)
        return [kernel_data]


class KBChannelwiseWeightOperator:
    """
    Channelwiseかつ1つのウェイトをとる処理
    """

    def __init__(self, func_name, sources, serial_generator, weight_offset):
        self.func_name = func_name
        self.sources = sources
        self.serial_generator = serial_generator
        self._weight_data_name = 'weight_data' + str(self.serial_generator.get())
        # meta_bufferのポインタを進め、self.meta_bufferの内容を読み取る
        self.post_init_source = """
const device float *{0} = weight_buffer + (*meta_buffer++);
        """.format(self._weight_data_name)
        self.meta_buffer = np.array([weight_offset], dtype=np.int32).tobytes()

    def wrap_expression(self, expression):
        return '{0}({1}, {2}[out_chid])'.format(self.func_name, expression, self._weight_data_name)


class KBElementwiseOperator:
    """
    Elementwiseかつウェイト不要の処理が他のレイヤーに後続する際のカーネル関数生成
    """

    def __init__(self, func_name, sources, serial_generator):
        self.func_name = func_name
        self.sources = sources
        self.post_init_source = """
        """  # 初期化不要
        self.meta_buffer = b''
        self.serial_generator = serial_generator

    def wrap_expression(self, expression):
        return '{0}({1})'.format(self.func_name, expression)


class KBBiasLayer(KBLayer):
    def __init__(self, layer: DNNLayer):
        super().__init__(layer, 'bias', {KBLayerAttribute.Channelwise})

    def get_channelwise_operator(self, weight_allocation: KBWeightAllocation,
                                 serial_generator: KBKernelSerialGenerator):
        weight_aw = weight_allocation.allocation[self.layer.name + '/b']
        return KBChannelwiseWeightOperator('channelwise_bias', {'channelwise_bias': channelwise_bias_source},
                                           serial_generator, weight_aw.offset)

    def generate_kernels(self, batch_size: int,
                         bottoms: List[DNNVariable], tops: List[DNNVariable],
                         weight_allocation: KBWeightAllocation, variable_allocation: KBVariableAllocation) -> List[
        KernelData]:
        raise NotImplementedError()


relu_source = """

kernel void relu(const device float *weight_buffer[[buffer(0)]],
                 device float *data_buffer[[buffer(1)]],
                 const device int *meta_buffer[[buffer(2)]],
                  uint index[[thread_position_in_grid]])
{
  device float *input_data = data_buffer + meta_buffer[0];
  device float *output_data = data_buffer + meta_buffer[1];
  const int n = meta_buffer[2];
    for (int gid = index; gid < n; gid += 4096) {
      float val = input_data[gid];
      if (val < 0.0) {
        val = 0.0;
      }
      output_data[gid] = val;
    }
}
"""


class KBReluLayer(KBLayer):
    def __init__(self, layer: DNNLayer):
        super().__init__(layer, 'relu', {KBLayerAttribute.Elementwise})

    def get_elementwise_operator(self, weight_allocation: KBWeightAllocation,
                                 serial_generator: KBKernelSerialGenerator):
        return KBElementwiseOperator('elementwise_relu', {'elementwise_relu': elementwise_relu_source},
                                     serial_generator)

    def generate_kernels(self, batch_size: int,
                         bottoms: List[DNNVariable], tops: List[DNNVariable],
                         weight_allocation: KBWeightAllocation, variable_allocation: KBVariableAllocation) -> List[
        KernelData]:
        layer = self.layer
        n = layer.parameters['out_size'] * batch_size
        bottom_av = variable_allocation.allocation[bottoms[0].name]
        top_av = variable_allocation.allocation[tops[0].name]
        meta_array = np.array([bottom_av.offset, top_av.offset, n], dtype=np.int32)
        meta_buffer = meta_array.tobytes()
        threadgroups_per_grid = {'width': 8, 'height': 1, 'depth': 1}
        threads_per_thread_group = {'width': 512, 'height': 1, 'depth': 1}
        kernel_data = KernelData({'relu': relu_source}, 'relu', threadgroups_per_grid, threads_per_thread_group,
                                 meta_buffer)
        return [kernel_data]


class KBLayerGenerator:
    @classmethod
    def generate(cls, layer: DNNLayer) -> KBLayer:
        if layer.layer_type == DNNLayerType.Linear:
            kb_layer = KBLinearLayer(layer)
        elif layer.layer_type == DNNLayerType.Bias:
            kb_layer = KBBiasLayer(layer)
        elif layer.layer_type == DNNLayerType.Relu:
            kb_layer = KBReluLayer(layer)
        else:
            raise ValueError('Unknown layer')
        return kb_layer
