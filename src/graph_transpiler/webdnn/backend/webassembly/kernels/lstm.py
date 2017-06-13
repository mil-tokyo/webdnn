from typing import List

from webdnn.backend.code_generator.allocator import MemoryLayout
from webdnn.backend.code_generator.injectors.kernel_name_injector import KernelNameInjector
from webdnn.backend.code_generator.injectors.meta_injector import MetaInjector
from webdnn.backend.webassembly.kernel import Kernel
from webdnn.graph.axis import Axis
from webdnn.graph.operators.lstm import LSTM
from webdnn.graph.order import OrderNC, OrderCN, OrderNT, OrderNTC

template = """
#ifndef INCLUDE_EIGEN
#define INCLUDE_EIGEN
#include <Eigen/Dense>
#endif

void %%FUNC_NAME%%(const int * %%META_NAME%%)
{
    const float *X = data_buffer + %%META_LOAD(lstm_X_offset)%%;
    float *Y = data_buffer + %%META_LOAD(lstm_Y_offset)%%;
    float *W_input = data_buffer + %%META_LOAD(lstm_W_input_offset)%%;
    float *W_hidden = data_buffer + %%META_LOAD(lstm_W_hidden_offset)%%;
    float *b = data_buffer + %%META_LOAD(lstm_b_offset)%%;
    const int input_dim = %%META_LOAD(lstm_input_dim)%%;
    const int sequence_len = %%META_LOAD(lstm_sequence_len)%%;
    const int batch_size = %%META_LOAD(lstm_batch_size)%%;
    const int hidden_dim = %%META_LOAD(lstm_hidden_dim)%%;
    const int hidden_dim4 = hidden_dim * 4;
    const int ofs_i = 0;
    const int ofs_f = hidden_dim * 1;
    const int ofs_c = hidden_dim * 2;
    const int ofs_o = hidden_dim * 3;
    
    auto activation = [](float x) {
        // hard sigmoid
        x = x * 0.2 + 0.5;
        if (x < 0.0) {
            x = 0.0;
        } else if (x > 1.0) {
            x = 1.0;
        }
        return x;
    };
    
    auto recurrent_activation = [](float x) {
        // tanh
        return tanhf(x);
    };
    
    float *mem_c = new float[hidden_dim * batch_size]();
    float *mem_h = new float[hidden_dim * batch_size]();
    float *mem_v = new float[hidden_dim4 * batch_size](); // i, f, c, o
    float *mem_x_t = new float[input_dim * batch_size]();
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_v(mem_v, batch_size, hidden_dim4);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_h(mem_h, batch_size, hidden_dim);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_x_t(mem_x_t, batch_size, input_dim);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_w_input(W_input, input_dim, hidden_dim4);
    Eigen::Map<Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> > mat_w_hidden(W_hidden, hidden_dim, hidden_dim4);
    Eigen::Map<Eigen::RowVectorXf > vec_b(b, hidden_dim4);

    for (int t = 0; t < sequence_len; t++) {
        // copy x of current time
        for (int n = 0; n < batch_size; n++) {
            for (int dim = 0; dim < input_dim; dim++) {
                mem_x_t[dim + n * input_dim] = X[(n * sequence_len + t) * input_dim + dim];
            }
        }
    
        mat_v.noalias() = mat_x_t * mat_w_input + mat_h * mat_w_hidden;
        mat_v.rowwise() += vec_b;
        
        for (int n = 0; n < batch_size; n++) {
            // update c, h
            for (int dim = 0; dim < hidden_dim; dim++) {
                float val_i = mem_v[dim + ofs_i + n * hidden_dim4];
                float val_f = mem_v[dim + ofs_f + n * hidden_dim4];
                float val_c = mem_v[dim + ofs_c + n * hidden_dim4];
                float val_o = mem_v[dim + ofs_o + n * hidden_dim4];
                val_i = activation(val_i);
                val_f = activation(val_f);
                float val_last_c = mem_c[dim + n * hidden_dim];
                val_c = recurrent_activation(val_c) * val_i + val_last_c * val_f;
                mem_c[dim + n * hidden_dim] = val_c;
                mem_h[dim + n * hidden_dim] = recurrent_activation(val_c) * activation(val_o);
            }
        }
    }
    
    // write output
    for (int i = 0; i < batch_size * hidden_dim; i++) {
        Y[i] = mem_h[i];
    }
    
    delete[] mem_c;
    delete[] mem_h;
    delete[] mem_v;
    delete[] mem_x_t;

}
"""


def lstm(op: LSTM, memory_layout: MemoryLayout) -> List[Kernel]:
    x = memory_layout[op.inputs["x"]]
    w_input = memory_layout[op.inputs["w_input"]]
    w_hidden = memory_layout[op.inputs["w_hidden"]]
    b = memory_layout[op.inputs["b"]]
    y = memory_layout[op.outputs["y"]]

    assert x.variable.order == OrderNTC
    assert w_input.variable.order == OrderCN
    assert w_hidden.variable.order == OrderCN
    assert y.variable.order == OrderNC

    # W is for updating i, f, c, o
    hidden_dim = w_hidden.variable.shape_dict[Axis.C]

    meta_injector = MetaInjector()
    meta_injector.register({
        "lstm_X_offset": x.offset,
        "lstm_Y_offset": y.offset,
        "lstm_W_input_offset": w_input.offset,
        "lstm_W_hidden_offset": w_hidden.offset,
        "lstm_b_offset": b.offset,
        "lstm_input_dim": x.variable.shape_dict[Axis.C],
        "lstm_sequence_len": x.variable.shape_dict[Axis.T],
        "lstm_batch_size": x.variable.shape_dict[Axis.N],
        "lstm_hidden_dim": hidden_dim
    })

    name_injector = KernelNameInjector(op)

    source = template
    source = meta_injector.inject(source)
    source = name_injector.inject(source)

    kernel = Kernel(
        {name_injector.name: source},
        name_injector.name,
        meta_injector.buffer
    )

    return [kernel]
