from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webgpu.generator import WebGPUDescriptorGenerator
from webdnn.backend.webgpu.kernel import Kernel, GPUSize
from webdnn.backend.webgpu.preset_placeholders import MAX_THREADS_PER_THREADGROUP
from webdnn.graph.axis import Axis
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNC, OrderNTC, OrderCN


def generate_template_general(initial_C: bool, initial_H: bool, return_sequences: bool,
                              activation_function: str, recurrent_activation_function: str):
    return """
kernel void %%FUNC_NAME%%(device float * %%STATIC_BUFFER%%[[buffer(0)]],
                          device float * %%DYNAMIC_BUFFER%%[[buffer(1)]],
                          const device int * %%META_BUFFER%%[[buffer(2)]],
                          uint global_index[[thread_position_in_grid]],
                          uint num_threads[[threads_per_grid]])
{
#define USE_INITIAL_C %%USE_INITIAL_C%%
#define USE_INITIAL_H %%USE_INITIAL_H%%
#define activation_function(x) %%ACTIVATION_FUNCTION%%
#define recurrent_activation_function(x) %%RECURRENT_ACTIVATION_FUNCTION%%
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
#if USE_INITIAL_H
    const device float  *initial_H = %%LOAD_BUFFER(lstm_initial_H)%%;
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
#if USE_INITIAL_H
        XH_H[gid] = initial_H[gid];
#else
        XH_H[gid] = 0;
#endif

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

        threadgroup_barrier(mem_flags::mem_device);

        //FIXME: replace here to more efficient sgemv implementation.
        // `4` means the number of hidden matrices (input, forget, activation, output).
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

        threadgroup_barrier(mem_flags::mem_device);

        for (int gid = global_index; gid < C2 * N; gid += num_threads)
        {
            const int n = gid % N;
            const int c2 = gid / N;

            float i = workspace[gid + N * C2 * 0];
            float f = workspace[gid + N * C2 * 1];
            float a = workspace[gid + N * C2 * 2];
            float o = workspace[gid + N * C2 * 3];
            float c = final_C[n * C2 + c2];

            i = recurrent_activation_function(i);
            f = recurrent_activation_function(f);
            a = activation_function(a);
            o = recurrent_activation_function(o);

            c = a * i + c * f;

            final_C[n * C2 + c2] = c;
            const float h = activation_function(c) * o;
            XH_H[gid] = h;

#if RETURN_SEQUENCES
            Y[(n * T + t) * C2 + c2] = h;
#endif
        }
    }

#if !RETURN_SEQUENCES
    //copy final output to output variable
    for (int gid = global_index; gid < C2 * N; gid += num_threads)
    {
        const int n = gid % N;
        const int c2 = gid / N;
        Y[n * C2 + c2] = XH_H[gid];
    }
#endif

#undef USE_INITIAL_C
#undef USE_INITIAL_H
#undef activation_function
#undef recurrent_activation_function
#undef RETURN_SEQUENCES
}
    """ \
        .replace("%%USE_INITIAL_C%%", "1" if initial_C else "0") \
        .replace("%%USE_INITIAL_H%%", "1" if initial_H else "0") \
        .replace("%%ACTIVATION_FUNCTION%%", activation_function) \
        .replace("%%RECURRENT_ACTIVATION_FUNCTION%%", recurrent_activation_function) \
        .replace("%%RETURN_SEQUENCES%%", "1" if return_sequences else "0")


@WebGPUDescriptorGenerator.register_handler(LSTM)
def lstm(op: LSTM, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    b = op.inputs["b"]
    y = op.outputs["y"]
    x_and_h = op.inputs["x_and_h"]
    w_all = op.inputs["w_all"]
    workspace = op.inputs["workspace"]
    final_c = op.outputs["final_c"]

    use_initial_c = op.parameters["use_initial_c"]
    use_initial_h = op.parameters["use_initial_h"]
    return_sequences = op.parameters["return_sequences"]

    assert x.order == OrderNTC, \
        f"Current implementation supports only OrderNTC for input variable order: x.order = {x.order}"

    if return_sequences:
        assert y.order == OrderNTC, f"Current implementation supports only OrderNTC for output variable of " + \
                                    f"LSTM in return_sequences=True mode: y.order = {y.order}"
    else:
        assert y.order == OrderNC, \
            f"Current implementation supports only OrderNC for output variable of LSTM " + \
            f"in return_sequences=False mode: y.order = {y.order}"

    assert w_all.order == OrderCN
    assert final_c.order == OrderNC

    N = x.shape_dict[Axis.N]
    T = x.shape_dict[Axis.T]
    C1 = x.shape_dict[Axis.C]
    C2 = y.shape_dict[Axis.C]

    buffer_injector = BufferInjector()
    buffer_injector.register({
        "lstm_X": memory_layout[x],
        "lstm_Y": memory_layout[y],
        "lstm_b": memory_layout[b],
        "lstm_N": N,
        "lstm_T": T,
        "lstm_C1": C1,
        "lstm_C2": C2,
        "lstm_X_and_H": memory_layout[x_and_h],
        "lstm_W_all": memory_layout[w_all],
        "lstm_workspace": memory_layout[workspace],
        "lstm_final_C": memory_layout[final_c],
        "lstm_initial_C": memory_layout[op.inputs["initial_c"]] if use_initial_c else 0,
        "lstm_initial_H": memory_layout[op.inputs["initial_h"]] if use_initial_h else 0,
    })

    name_injector = KernelNameInjector(op)

    if op.parameters["activation"] == "tanh":
        activation_function = "(metal::precise::tanh(x))"
    else:
        raise NotImplementedError

    if op.parameters["recurrent_activation"] == "hard_sigmoid":
        recurrent_activation_function = "((x) < -2.5 ? 0.0 : ((x) > +2.5 ? 1.0 : ((x) * 0.2 + 0.5)))"
    elif op.parameters["recurrent_activation"] == "sigmoid":
        recurrent_activation_function = "(metal::precise::tanh(0.5f * (x)) * 0.5f + 0.5f)"
    else:
        raise NotImplementedError

    source = generate_template_general(use_initial_c, use_initial_h, return_sequences, activation_function, recurrent_activation_function)
    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        GPUSize(1, 1, 1),
        GPUSize(MAX_THREADS_PER_THREADGROUP, 1, 1),
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
