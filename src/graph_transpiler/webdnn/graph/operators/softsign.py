from webdnn.graph.operators.elementwise import Elementwise


class Softsign(Elementwise):
    """Softsign activation

    https://www.tensorflow.org/api_docs/python/tf/nn/softsign
    x / (abs(x) + 1)

    Args:
        name (str): Operator name.

    """
    pass
