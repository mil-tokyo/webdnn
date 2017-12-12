from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.buffer_injector import BufferInjector
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.webassembly.generator import WebassemblyDescriptorGenerator
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNC, OrderCN, OrderNTC

template = """
#ifndef INCLUDE_EIGEN
#define INCLUDE_EIGEN
#include <Eigen/Dense>
#endif

void %%FUNC_NAME%%(const int * %%META_BUFFER%%)
{
%%DEFINE_SEQUENCE_OUTPUT%%
    const float *X = %%LOAD_BUFFER(lstm_X)%%;
    float *Y = %%LOAD_BUFFER(lstm_Y)%%;
    float *mem_c = %%LOAD_BUFFER(lstm_final_c)%%;
    float *W_input = %%LOAD_BUFFER(lstm_W_input)%%;
    float *W_hidden = %%LOAD_BUFFER(lstm_W_hidden)%%;
    const int input_dim = %%LOAD_BUFFER(lstm_input_dim)%%;
    const int sequence_len = %%LOAD_BUFFER(lstm_sequence_len)%%;
    const int batch_size = %%LOAD_BUFFER(lstm_batch_size)%%;
    const int hidden_dim = %%LOAD_BUFFER(lstm_hidden_dim)%%;
    const int hidden_dim4 = hidden_dim * 4;
    const int ofs_i = 0;
    const int ofs_f = hidden_dim * 1;
    const int ofs_c = hidden_dim * 2;
    const int ofs_o = hidden_dim * 3;
    %%BIAS_INITIALIZER%%

    auto activation = [](float x) {
        %%ACTIVATION_CORE%%
    };

    auto recurrent_activation = [](float x) {
        %%RECURRENT_ACTIVATION_CORE%%
    };

    %%INITIAL_C_COPIER%%
    float *mem_h = new float[hidden_dim * batch_size]();
    %%INITIAL_H_COPIER%%
    float *mem_v = new float[hidden_dim4 * batch_size](); // i, f, c, o
    float *mem_x_t = new float[input_dim * batch_size]();
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_v(mem_v, batch_size, hidden_dim4);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_h(mem_h, batch_size, hidden_dim);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_x_t(mem_x_t, batch_size, input_dim);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_w_input(W_input, input_dim, hidden_dim4);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_w_hidden(W_hidden, hidden_dim, hidden_dim4);

    for (int t = 0; t < sequence_len; t++) {
        // copy x of current time
        for (int n = 0; n < batch_size; n++) {
            for (int dim = 0; dim < input_dim; dim++) {
                mem_x_t[dim + n * input_dim] = X[(n * sequence_len + t) * input_dim + dim];
            }
        }

        mat_v.noalias() = mat_x_t * mat_w_input + mat_h * mat_w_hidden;
        %%BIAS_APPLIER%%

        for (int n = 0; n < batch_size; n++) {
            // update c, h
            for (int dim = 0; dim < hidden_dim; dim++) {
                float val_i = mem_v[dim + ofs_i + n * hidden_dim4];
                float val_f = mem_v[dim + ofs_f + n * hidden_dim4];
                float val_c = mem_v[dim + ofs_c + n * hidden_dim4];
                float val_o = mem_v[dim + ofs_o + n * hidden_dim4];
                val_i = recurrent_activation(val_i);
                val_f = recurrent_activation(val_f);
                float val_last_c = mem_c[dim + n * hidden_dim];
                val_c = activation(val_c) * val_i + val_last_c * val_f;
                mem_c[dim + n * hidden_dim] = val_c;
                mem_h[dim + n * hidden_dim] = activation(val_c) * recurrent_activation(val_o);
            }
        }

        //write output on sequence
#ifdef SEQUENCE_OUTPUT
        for (int n = 0; n < batch_size; n++) {
            for (int dim = 0; dim < hidden_dim; dim++) {
                Y[(n * sequence_len + t) * hidden_dim + dim] = mem_h[n * hidden_dim + dim];
            }
        }
#endif
    }

    // write output
#ifndef SEQUENCE_OUTPUT
    for (int i = 0; i < batch_size * hidden_dim; i++) {
        Y[i] = mem_h[i];
    }
#endif

    delete[] mem_h;
    delete[] mem_v;
    delete[] mem_x_t;
#undef SEQUENCE_OUTPUT
}
"""


@WebassemblyDescriptorGenerator.register_handler(LSTM)
def lstm(op: LSTM, memory_layout: MemoryLayout) -> List[Kernel]:
    x = op.inputs["x"]
    w_input = op.inputs["w_input"]
    w_hidden = op.inputs["w_hidden"]
    y = op.outputs["y"]
    final_c = op.outputs["final_c"]

    assert x.order == OrderNTC
    assert w_input.order == OrderCN
    assert w_hidden.order == OrderCN
    if op.parameters["return_sequences"]:
        assert y.order == OrderNTC
    else:
        assert y.order == OrderNC
    assert final_c.order == OrderNC

    # W is for updating i, f, c, o
    hidden_dim = w_hidden.shape_dict[Axis.C]

    buffer_injector_items = {
        "lstm_X": memory_layout[x],
        "lstm_Y": memory_layout[y],
        "lstm_final_c": memory_layout[final_c],
        "lstm_W_input": memory_layout[w_input],
        "lstm_W_hidden": memory_layout[w_hidden],
        "lstm_input_dim": x.shape_dict[Axis.C],
        "lstm_sequence_len": x.shape_dict[Axis.T],
        "lstm_batch_size": x.shape_dict[Axis.N],
        "lstm_hidden_dim": hidden_dim
    }

    source = template
    if op.parameters["return_sequences"]:
        source = source.replace("%%DEFINE_SEQUENCE_OUTPUT%%", "#define SEQUENCE_OUTPUT")
    else:
        source = source.replace("%%DEFINE_SEQUENCE_OUTPUT%%", "")

    if op.parameters["use_bias"]:
        b = op.inputs["b"]
        buffer_injector_items["lstm_b"] = memory_layout[b]
        source = source.replace("%%BIAS_INITIALIZER%%",
                                "float *b = %%LOAD_BUFFER(lstm_b)%%;\nEigen::Map<Eigen::RowVectorXf > vec_b(b, hidden_dim4);")
        source = source.replace("%%BIAS_APPLIER%%", "mat_v.rowwise() += vec_b;")
    else:
        source = source.replace("%%BIAS_INITIALIZER%%", "")
        source = source.replace("%%BIAS_APPLIER%%", "")

    if op.parameters["use_initial_c"]:
        initial_c = op.inputs["initial_c"]
        buffer_injector_items["lstm_initial_c"] = memory_layout[initial_c]
        source = source.replace("%%INITIAL_C_COPIER%%", """
        const float *initial_c = %%LOAD_BUFFER(lstm_initial_c)%%;
        for (int i = 0; i < hidden_dim * batch_size; i++) {
            mem_c[i] = initial_c[i];
        }
        """)
    else:
        source = source.replace("%%INITIAL_C_COPIER%%", """
        for (int i = 0; i < hidden_dim * batch_size; i++) {
            mem_c[i] = 0.0F;
        }
        """)

    if op.parameters["use_initial_h"]:
        initial_h = op.inputs["initial_h"]
        buffer_injector_items["lstm_initial_h"] = memory_layout[initial_h]
        source = source.replace("%%INITIAL_H_COPIER%%", """
        const float *initial_h = %%LOAD_BUFFER(lstm_initial_h)%%;
        for (int i = 0; i < hidden_dim * batch_size; i++) {
            mem_h[i] = initial_h[i];
        }
        """)
    else:
        source = source.replace("%%INITIAL_H_COPIER%%", "")

    if op.parameters["activation"] == "tanh":
        source = source.replace("%%ACTIVATION_CORE%%", """
        return tanhf(x);
        """)
    else:
        raise NotImplementedError

    if op.parameters["recurrent_activation"] == "hard_sigmoid":
        source = source.replace("%%RECURRENT_ACTIVATION_CORE%%", """
        x = x * 0.2F + 0.5F;
        if (x < 0.0F) {
            x = 0.0F;
        } else if (x > 1.0F) {
            x = 1.0F;
        }
        return x;
        """)
    elif op.parameters["recurrent_activation"] == "sigmoid":
        source = source.replace("%%RECURRENT_ACTIVATION_CORE%%", """
        x = 1.0F / (1.0 + expf(-x));
        return x;
        """)
    else:
        raise NotImplementedError

    buffer_injector = BufferInjector()
    buffer_injector.register(buffer_injector_items)

    name_injector = KernelNameInjector(op)

    source = buffer_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        buffer_injector.buffer,
        buffer_injector.unresolved_value_list
    )

    return [kernel]
