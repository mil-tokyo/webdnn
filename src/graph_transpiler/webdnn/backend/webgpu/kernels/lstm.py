from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.graph.axis import Axis
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNC, OrderNTC, OrderCN


def generate_template_general(initial_C: bool, return_sequences: bool):
    return """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%%[[buffer(2)]],
                          uint global_index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
#define USE_INITIAL_C %%USE_INITIAL_C%%
#define RETURN_SEQUENCES %%RETURN_SEQUENCES%%

    const device float  *X         = %%LOAD_BUFFER(lstm_X)%%;
          device float  *XH        = %%LOAD_BUFFER(lstm_X_and_H)%%;
    const device float  *W_all     = %%LOAD_BUFFER(lstm_W_all)%%;
          device float  *workspace = %%LOAD_BUFFER(lstm_workspace)%%;
          device float  *Y         = %%LOAD_BUFFER(lstm_Y)%%;
          device float  *final_C   = %%LOAD_BUFFER(lstm_final_C)%%;
    const device float  *b         = %%LOAD_BUFFER(lstm_b)%%;

#if USE_INITIAL_C
        const device float  *initial_C = %%LOAD_BUFFER(lstm_initial_C)%%;
#endif

    const int N  = %%LOAD_BUFFER(lstm_N)%%;
    const int T  = %%LOAD_BUFFER(lstm_T)%%;
    const int C1 = %%LOAD_BUFFER(lstm_C1)%%;
    const int C2 = %%LOAD_BUFFER(lstm_C2)%%;

    device float *XH_X = XH;
    device float *XH_H = XH + C1 * N;

    //reset output and cell state
    for (int gid = global_index; gid < N * C2; gid += num_threads)
    {
        XH_H[gid] = 0;

#if USE_INITIAL_C
        final_C[gid] = initial_C[gid];
#else
        final_C[gid] = 0;
#endif
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
                v += XH[c1c2 * N + n] * W_all[c1c2 * C2 * 4 + c2_4]; 
            }
            
            workspace[gid] = v;
        }
        
        //threadgroup_barrier(mem_flags::mem_device);

        for (int gid = global_index; gid < C2 * N; gid += num_threads)
        {
            float i = workspace[gid + N * C2 * 0];
            float f = workspace[gid + N * C2 * 1];
            float a = workspace[gid + N * C2 * 2];
            float o = workspace[gid + N * C2 * 3];
            float cell_last = final_C[gid];

            i = i < -2.5 ? 0.0 : (i > +2.5 ? 1.0 : (i * 0.2 + 0.5));
            f = f < -2.5 ? 0.0 : (f > +2.5 ? 1.0 : (f * 0.2 + 0.5));
            a = tanh(a);
            o = o < -2.5 ? 0.0 : (o > +2.5 ? 1.0 : (o * 0.2 + 0.5));
    
            cell_last = a * i + cell_last * f;

            final_C[gid] = cell_last;
            const float h = tanh(cell_last) * o;
            XH_H[gid] = h;

#if RETURN_SEQUENCES
            const int n = gid % N;
            const int c2 = gid / C2;
            Y[(n * T + t) * C2 + c2] = h;
#endif
        }
    }

#if !RETURN_SEQUENCES
    //copy final output to output variable
    for (int gid = global_index; gid < C2 * N; gid += num_threads)
    {
        Y[gid] = XH_H[gid];
    }
#endif

#undef USE_INITIAL_C
#undef RETURN_SEQUENCES
}
    """ \
        .replace("%%USE_INITIAL_C%%", "1" if initial_C else "0") \
        .replace("%%RETURN_SEQUENCES%%", "1" if return_sequences else "0")


def lstm(op: LSTM, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    b = memory_layout[op.inputs["b"]]
    y = memory_layout[op.outputs["y"]]
    x_and_h = memory_layout[op.inputs["x_and_h"]]
    w_all = memory_layout[op.inputs["w_all"]]
    workspace = memory_layout[op.inputs["workspace"]]
    final_c = memory_layout[op.outputs["final_c"]]

    use_initial_c = op.parameters["use_initial_c"]
    return_sequences = op.parameters["return_sequences"]

    assert x.variable.order == OrderNTC, \
        f"Current implementation supports only OrderNTC for input variable order: x.order = {x.variable.order}"

    if return_sequences:
        assert y.variable.order == OrderNTC, f"Current implementation supports only OrderNTC for output variable of " + \
                                             "LSTM in return_sequences=True mode: y.order = {y.variable.order}"
    else:
        assert y.variable.order == OrderNC, \
            f"Current implementation supports only OrderNC for output variable of LSTM " + \
            f"in return_sequences=False mode: y.order = {y.variable.order}"

    assert w_all.variable.order == OrderCN

    N = x.variable.shape_dict[Axis.N]
    T = x.variable.shape_dict[Axis.T]
    C1 = x.variable.shape_dict[Axis.C]
    C2 = y.variable.shape_dict[Axis.C]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "lstm_X": x,
        "lstm_Y": y,
        "lstm_b": b,
        "lstm_N": N,
        "lstm_T": T,
        "lstm_C1": C1,
        "lstm_C2": C2,
        "lstm_X_and_H": x_and_h,
        "lstm_W_all": w_all,
        "lstm_workspace": workspace,
        "lstm_final_C": final_c,
        "lstm_initial_C": memory_layout[op.inputs["initial_c"]] if use_initial_c else 0,
    })

    name_injector = KernelNameInjector(op)

    source = generate_template_general(use_initial_c, return_sequences)
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(1, 1, 1),
        GPUSize(32, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
