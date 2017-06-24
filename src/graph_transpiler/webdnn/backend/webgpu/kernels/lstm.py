from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.attributes.lstm_optimized import LSTMOptimized
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.axis import Axis
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNC, OrderNTC, OrderCN

template_basic = """
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

template_optimized = """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%%[[buffer(2)]],
                          uint global_index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
    const device float  *X         = %%LOAD_BUFFER(lstm_X)%%;
          device float  *XH        = %%LOAD_BUFFER(lstm_X_and_H)%%;
    const device float  *W_all     = %%LOAD_BUFFER(lstm_W_all)%%;
          device float  *cell      = %%LOAD_BUFFER(lstm_cell)%%;
          device float  *workspace = %%LOAD_BUFFER(lstm_workspace)%%;
          device float  *Y         = %%LOAD_BUFFER(lstm_Y)%%;
    const device float  *b         = %%LOAD_BUFFER(lstm_b)%%;

    const int N  = %%LOAD_BUFFER(lstm_N)%%;
    const int T  = %%LOAD_BUFFER(lstm_T)%%;
    const int C1 = %%LOAD_BUFFER(lstm_C1)%%;
    const int C2 = %%LOAD_BUFFER(lstm_C2)%%;

    device float *XH_X = XH;
    device float *XH_H = XH + N * C1;

    //reset output and cell state
    for (int gid = global_index; gid < N * C2; gid += num_threads)
    {
        XH_H[gid] = 0;
        cell[gid] = 0;
    }
    
    for (int t = 0; t < T; t++) 
    {
        for (int gid = global_index; gid < C1 * N; gid += num_threads)
        {
            const int n = gid % N;
            const int c1 = gid / N;
            XH_X[gid] = X[(n * T + t) * C1 + c1];
        }
        
        //FIXME: replace here to more efficient sgemv implementation.
        for (int gid = global_index; gid < C2 * 4 * N; gid += num_threads)
        {
            const int n = gid % N;
            const int c2_4 = gid / N;
            
            float v = b[c2_4];
            
            for (int c1c2 = 0; c1c2 < C1 + C2; c1c2++)
            {
                v += XH[n * (C1 + C2) + c1c2] * W_all[c1c2 * C2 * 4 + c2_4]; 
            }
            
            workspace[gid] = v;
        }
        
        threadgroup_barrier(mem_flags::mem_device);

        for (int gid = global_index; gid < C2 * N; gid += num_threads)
        {
            float i = workspace[gid + N * C2 * 0];
            float f = workspace[gid + N * C2 * 1];
            float a = workspace[gid + N * C2 * 2];
            float o = workspace[gid + N * C2 * 3];
            float cell_last = cell[gid];

            i = i < -2.5 ? 0.0 : (i > +2.5 ? 1.0 : (i * 0.2 + 0.5));
            f = f < -2.5 ? 0.0 : (f > +2.5 ? 1.0 : (f * 0.2 + 0.5));
            a = tanh(a);
            o = o < -2.5 ? 0.0 : (o > +2.5 ? 1.0 : (o * 0.2 + 0.5));
    
            cell_last = a * i + cell_last * f;

            cell[gid] = cell_last;
            XH_H[gid] = tanh(cell_last) * o;
        }
    }
    
    //copy final output to output variable
    for (int gid = global_index; gid < C2 * N; gid += num_threads)
    {
        Y[gid] = XH_H[gid];
    }
}
"""


def lstm(op: LSTM, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    b = memory_layout[op.inputs["b"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNTC, \
        f"Current implementation supports only OrderNTC for input variable order: x.order = {x.variable.order}"
    assert y.variable.order == OrderNC, \
        f"Current implementation supports only OrderNC for output variable order: y.order = {y.variable.order}"

    N = x.variable.shape_dict[Axis.N]
    T = x.variable.shape_dict[Axis.T]
    C1 = x.variable.shape_dict[Axis.C]
    C2 = y.variable.shape_dict[Axis.C]

    flag_optimized = op.has_attribute(LSTMOptimized)

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "lstm_X": x,
        "lstm_Y": y,
        "lstm_b": b,
        "lstm_N": N,
        "lstm_T": T,
        "lstm_C1": C1,
        "lstm_C2": C2
    })

    name_injector = KernelNameInjector(op)

    if flag_optimized:
        x_and_h = memory_layout[op.inputs["x_and_h"]]
        w_all = memory_layout[op.inputs["w_all"]]
        workspace = memory_layout[op.inputs["workspace"]]
        cell = memory_layout[op.inputs["cell"]]

        assert w_all.variable.order == OrderCN

        buffer_injector.register({
            "lstm_X_and_H": x_and_h,
            "lstm_W_all": w_all,
            "lstm_workspace": workspace,
            "lstm_cell": cell
        })
        source = template_optimized

    else:
        w_input = memory_layout[op.inputs["w_input"]]
        w_hidden = memory_layout[op.inputs["w_hidden"]]

        assert w_input.variable.order == OrderCN
        assert w_hidden.variable.order == OrderCN

        buffer_injector.register({
            "lstm_W_input": w_input,
            "lstm_W_hidden": w_hidden,
        })
        source = template_basic

    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(1, 1, 1),
        GPUSize(1024 if C2 > 1024 else C2, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
