from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.axis import Axis
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNC, OrderNTC, OrderCN

template = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%%[[buffer(2)]],
                          ushort global_index[[thread_position_in_grid]])
{
    const device float  *X = %%LOAD_BUFFER(lstm_X)%%;
    const device float  *W_input = %%LOAD_BUFFER(lstm_W_input)%%;
    const device float  *W_hidden = %%LOAD_BUFFER(lstm_W_hidden)%%;
    device float        *Y = %%LOAD_BUFFER(lstm_Y)%%;
    const device float  *b = %%LOAD_BUFFER(lstm_b)%%;
    
    const int N  = %%LOAD_BUFFER(lstm_N)%%;
    const int T  = %%LOAD_BUFFER(lstm_T)%%;
    const int C1 = %%LOAD_BUFFER(lstm_C1)%%;
    const int C2 = %%LOAD_BUFFER(lstm_C2)%%;
    const int C2_4 = C2 * 4;
    
    const int n = 0;
    const int c2 = (int)global_index;
    
    //reset output and cell state
    float cell_last = 0.0;
    Y[c2] = 0;

    for (int t = 0; t < T; t++) {
        float i = b[c2 + C2 * 0];
        float f = b[c2 + C2 * 1];
        float a = b[c2 + C2 * 2];
        float o = b[c2 + C2 * 3];

        threadgroup_barrier(mem_flags::mem_device);

        for (int c = 0; c < C1; c++)
        {
            const float x = X[(n * T + t) * C1 + c];
            i += x * W_input[c * C2_4 + c2 + C2 * 0];
            f += x * W_input[c * C2_4 + c2 + C2 * 1];
            a += x * W_input[c * C2_4 + c2 + C2 * 2];
            o += x * W_input[c * C2_4 + c2 + C2 * 3];
        }
        
        for (int c = 0; c < C2; c++)
        {   
            const float y = Y[n * C2 + c];
            i += y * W_hidden[c * C2 * 4 + c2 + C2 * 0];
            f += y * W_hidden[c * C2 * 4 + c2 + C2 * 1];
            a += y * W_hidden[c * C2 * 4 + c2 + C2 * 2];
            o += y * W_hidden[c * C2 * 4 + c2 + C2 * 3];
        }

        i = i * 0.2 + 0.5;
        f = f * 0.2 + 0.5;
        o = o * 0.2 + 0.5;
        
        i = i < 0.0 ? 0.0 : (i > 1.0 ? 1.0 : i);
        f = f < 0.0 ? 0.0 : (f > 1.0 ? 1.0 : f);
        o = o < 0.0 ? 0.0 : (o > 1.0 ? 1.0 : o);

        a = tanh(a);
        
        cell_last = a * i + cell_last * f;
        Y[c2] = tanh(cell_last) * o;
    }
}
"""


def lstm(op: LSTM, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    w_input = memory_layout[op.inputs["w_input"]]
    w_hidden = memory_layout[op.inputs["w_hidden"]]
    b = memory_layout[op.inputs["b"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNTC, \
        f"Current implementation supports only OrderNTC for input variable order: x.order = {x.variable.order}"
    assert w_input.variable.order == OrderCN
    assert w_hidden.variable.order == OrderCN
    assert y.variable.order == OrderNC, \
        f"Current implementation supports only OrderNC for output variable order: y.order = {y.variable.order}"

    N = x.variable.shape_dict[Axis.N]
    T = x.variable.shape_dict[Axis.T]
    C1 = w_input.variable.shape_dict[Axis.C]
    C2 = w_hidden.variable.shape_dict[Axis.C]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "lstm_X": x,
        "lstm_W_input": w_input,
        "lstm_W_hidden": w_hidden,
        "lstm_Y": y,
        "lstm_b": b,
        "lstm_N": N,
        "lstm_T": T,
        "lstm_C1": C1,
        "lstm_C2": C2
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(1, 1, 1),
        GPUSize(C2, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
