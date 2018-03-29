def SquareLayer(shape, pos, array1_shape, array1):
    pn = pos[0]
    pc = pos[1]
    x = array1[pn, pc]
    y = x ** 2.0
    return y
