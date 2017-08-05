from webdnn.frontend.constraints import unify, add_placeholder_constraint
from webdnn.graph.variable import Variable


def check_broadcast_constraints(a: Variable, b: Variable):
    i_a = a.ndim - 1
    i_b = b.ndim - 1
    while i_a >= 0 and i_b >= 0:
        if a.shape[i_a] == b.shape[i_b] or a.shape[i_a] == 1 or b.shape[i_b] == 1:
            unify(a.order.axes[i_a], b.order.axes[i_b])

            if (a.shape[i_a] == 1 and b.shape[i_b] == 1) or (a.shape[i_a] != 1 and b.shape[i_b] != 1):
                # If broadcast is not occurred, size must be same
                add_placeholder_constraint(a.shape[i_a], b.shape[i_b])

            i_a -= 1
            i_b -= 1

        else:
            raise ValueError(f"Broadcast is failed: (a.shape)={a.shape}, (b.shape)={b.shape}")
